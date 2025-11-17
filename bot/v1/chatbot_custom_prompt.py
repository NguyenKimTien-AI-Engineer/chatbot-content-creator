from dotenv import load_dotenv
import threading
import json
import uuid
import time
import os
import asyncio
import re
import httpx

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.data import clean, history as _history, context_reduce
from controllers.llm import token as _token
from controllers.rag import retriever
from controllers.ultils import time as time_utils
from controllers.modules import reference
from controllers.databases.nosql.mongodb import MongoDBManager, get_mongodb_manager

from configs import environment, constant
from configs.prompts.custom import prompt_chatbot_custom, template_content, checklist, system

load_dotenv()


def extract_product_names_from_query(query: str) -> list:
    """
    Trích xuất tên sản phẩm từ câu truy vấn của người dùng.
    
    Args:
        query: Câu truy vấn của người dùng
        
    Returns:
        list: Danh sách các tên sản phẩm có thể được nhắc đến
    """
    # Danh sách các từ khóa phổ biến cho sản phẩm túi
    product_keywords = [
        'túi', 'bag', 'ví', 'sản phẩm', 'wallet', 'giày', 'shoes',
        'jen', 'mini', 'maxi', 'medium', 'small', 'large',
        'đen', 'đỏ', 'trắng', 'xanh', 'nâu', 'hồng', 'vàng',
        'da', 'canvas', 'vải', 'leather', 'cotton'
    ]
    
    # Tách từ và loại bỏ dấu câu
    words = re.findall(r'\b\w+\b', query.lower())
    
    # Tìm các từ khóa sản phẩm
    product_words = [word for word in words if word in product_keywords]
    
    # Nếu tìm thấy từ khóa sản phẩm, tạo các tổ hợp có thể
    if product_words:
        # Tách các từ trong câu truy vấn
        potential_names = []
        
        # Tìm các cụm từ có thể là tên sản phẩm
        # Ví dụ: "jen mini màu đen" -> ["jen mini", "jen", "mini"]
        words_clean = query.lower().split()
        
        # Tạo các tổ hợp 2-3 từ liên tiếp
        for i in range(len(words_clean)):
            for j in range(i+1, min(i+4, len(words_clean)+1)):
                phrase = ' '.join(words_clean[i:j])
                if len(phrase) > 2:  # Bỏ qua các từ quá ngắn
                    potential_names.append(phrase)
        
        return potential_names[:5]  # Giới hạn 5 tên tiềm năng
    
    return []


async def search_products_qdrant(query: str, limit: int = 3) -> str:
    """
    Tìm kiếm sản phẩm trong Qdrant kat_products collection.
    
    Args:
        query: Câu truy vấn tìm kiếm
        limit: Số lượng kết quả tối đa
        
    Returns:
        str: Thông tin sản phẩm được format
    """
    
    async def extract_product_phrase_ai(text: str) -> str:
        """Sử dụng OpenAI để tách cụm sản phẩm cần truy xuất từ query."""
        try:
            system_msg = (
                "Bạn là công cụ trích xuất cụm từ sản phẩm bằng tiếng Việt. "
                "Nếu câu hỏi chứa túi/ví/giày, trả về DUY NHẤT cụm từ mô tả sản phẩm để truy xuất (ví dụ: 'túi Lea màu beige'). "
                "Yêu cầu: ngắn gọn, không giải thích, không thêm dấu, giữ nguyên tên/màu/chất liệu nếu có. "
                "Nếu không có cụm cần truy xuất, trả về chuỗi rỗng."
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_msg),
                ("user", "{query}")
            ])

            chain = prompt | environment.get_llm(model=constant.MODEL_CHATBOT_SUGGESTION) | StrOutputParser()
            phrase = await chain.ainvoke({"query": text})

            if not isinstance(phrase, str):
                return ""

            phrase_clean = phrase.strip().strip('"').strip("'")
            phrase_clean = phrase_clean.splitlines()[0]
            return phrase_clean
        except Exception as err:
            print(f"Lỗi AI tách cụm sản phẩm: {err}")
            return ""

    try:
        # Gọi API tìm kiếm sản phẩm từ Qdrant
        url = f"{constant.SERVER_ADDRESS}/api/v1/search-products-qdrant"
        
        # Dùng AI để tách cụm sản phẩm cần truy xuất
        extracted = await extract_product_phrase_ai(query)
        effective_query = extracted if extracted else query
        if extracted:
            print(f"🧠 AI trích xuất cụm truy xuất: '{extracted}'")
        
        payload = {
            "user_id": "system",
            "query": effective_query,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                products_data = data.get("data", [])
                
                if not products_data:
                    return ""
                
                # Format kết quả tìm kiếm
                context = f"\n=== THÔNG TIN SẢN PHẨM TỪ QDRANT (tìm kiếm: '{query}') ===\n"
                
                for i, product in enumerate(products_data, 1):
                    content = product.get("content", "")
                    metadata = product.get("metadata", {})
                    score = product.get("score", 0)
                    
                    product_info = f"""
Sản phẩm {i} (Độ tương đồng: {score:.3f}):
Nội dung: {content}
Metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}
---
"""
                    context += product_info
                
                return context
            else:
                print(f"Lỗi khi tìm kiếm sản phẩm từ Qdrant: {response.status_code} - {response.text}")
                return ""
                
    except Exception as e:
        print(f"Lỗi khi tìm kiếm sản phẩm từ Qdrant: {e}")
        return ""


async def get_product_context(query: str, limit: int = 5) -> str:
    """
    Lấy thông tin sản phẩm từ database dựa trên query.
    
    Args:
        query: Câu truy vấn của người dùng
        limit: Số lượng sản phẩm tối đa để lấy
        
    Returns:
        str: Thông tin sản phẩm được format để thêm vào context
    """
    try:
        # Khởi tạo MongoDB manager
        db = MongoDBManager()
        
        # Tìm kiếm sản phẩm theo query
        products = await db.search_products(query=query, limit=limit)
        
        if not products:
            return ""
        
        # Format product information
        product_context = "\n=== THÔNG TIN SẢN PHẨM ===\n"
        
        for product in products:
            name = product.get('name', 'Không có tên')
            sku = product.get('sku', 'Không có SKU')
            
            # Lấy thông tin pricing
            pricing = product.get('pricing', {})
            price = pricing.get('price', 0)
            currency = pricing.get('currency', 'VND')
            
            # Lấy thông tin data
            data = product.get('data', {})
            description = data.get('description', 'Không có mô tả')
            category = data.get('category', [])
            quantity = data.get('quantity', 0)
            
            # Lấy media URLs
            media = product.get('media', [])
            image_urls = [m.get('url', '') for m in media if m.get('type') == 'image']
            
            product_info = f"""
Tên sản phẩm: {name}
Mã SKU: {sku}
Giá: {price:,} {currency}
Mô tả: {description}
Danh mục: {', '.join(category) if category else 'Chưa phân loại'}
Tồn kho: {quantity}
Hình ảnh: {', '.join(image_urls) if image_urls else 'Không có hình ảnh'}
---
"""
            product_context += product_info
        
        return product_context
        
    except Exception as e:
        print(f"Lỗi khi lấy thông tin sản phẩm: {e}")
        return ""


############################################################################################################
def chatbot_custom_prompt_stream(user_id, query, collections, session_id, history_id, system_instruction_user: str = "", include_products: bool = True):
    # query_ = asyncio.run(translate.translate_to_english(query))
    start_time = time.time()

    retrievers, references = retriever.get_retriever_reference_qdrant(collections, query, k=constant.K_CHATBOT_CUSTOM_PROMPT)

    contexts = clean.clean_special_characters(retrievers)

    # Lấy thông tin sản phẩm nếu được yêu cầu
    product_context = "Không có thông tin sản phẩm"  # Giá trị mặc định
    if include_products:
        try:
            # Tạo event loop mới cho async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Kiểm tra xem có tên sản phẩm trong query không
            product_names = extract_product_names_from_query(query)
            
            if product_names:
                print(f"🔍 Phát hiện tên sản phẩm trong query: {product_names}")
                # Nếu có tên sản phẩm, tìm kiếm trong Qdrant
                qdrant_results = loop.run_until_complete(search_products_qdrant(query))
                if qdrant_results:
                    product_context = qdrant_results
                    print(f"✅ Tìm thấy {len(qdrant_results.split('---')) - 1} sản phẩm từ Qdrant")
                else:
                    # Nếu không tìm thấy trong Qdrant, thử tìm trong MongoDB
                    product_context = loop.run_until_complete(get_product_context(query))
                    print("✅ Tìm kiếm trong MongoDB")
            else:
                # Không phát hiện tên sản phẩm, tìm kiếm thông thường trong MongoDB
                product_context = loop.run_until_complete(get_product_context(query))
                print("🔍 Không phát hiện tên sản phẩm, tìm kiếm trong MongoDB")
            
            loop.close()
            
            # Không thêm product_context vào contexts nữa vì nó được truyền riêng như biến text
            # if product_context:
            #     contexts = f"{contexts}\n{product_context}"
            
        except Exception as e:
            print(f"Lỗi khi lấy thông tin sản phẩm: {e}")
            # Tiếp tục mà không có product context nếu có lỗi
            product_context = "Không có thông tin sản phẩm"
    
    else:
        # Nếu include_products = False, đặt giá trị mặc định
        product_context = "Không có thông tin sản phẩm"

    if session_id == "":
        session_id = str(uuid.uuid4())

    history_context = _history.get_history_context(user_id, query, session_id)

    current_time = time_utils.get_current_vn_time()

    contexts, num_token_input = context_reduce.context_reduce(contexts, constant.MODEL_CHATBOT_CUSTOM_PROMPT)

    # print("⚙️ Prompt: ", _prompt)

    # Lấy system prompt từ file system.py và làm sạch
    system_prompt = clean.clean_special_characters(system.system)
    # Làm sạch system_instruction_user do người dùng nhập
    system_instruction_user = clean.clean_special_characters(str(system_instruction_user or ""))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_chatbot_custom.CHATBOT),
        ]
    )

    # Create the message payload that will be sent to the prompt
    message_payload = {
        "system": str(system_prompt), 
        "template": str(template_content.template), 
        "question": str(query), 
        "context": str(contexts), 
        "history": str(history_context), 
        "time_now": str(current_time),
        "checklist": str(checklist.checklist),
        "text": str(product_context),
        "system_instruction_user": str(system_instruction_user),
    }

    # Debug logging - set DEBUG_PROMPT=True to see full prompt
    DEBUG_PROMPT = os.environ.get('DEBUG_PROMPT', 'False').lower() == 'true'
    
    if DEBUG_PROMPT:
        # Format the full prompt for debugging
        full_prompt = prompt_chatbot_custom.CHATBOT.format(**message_payload)
        
        # Print the full prompt for debugging
        print("=" * 80)
        print("🔍 FULL PROMPT DEBUG OUTPUT:")
        print("=" * 80)
        print(full_prompt)
        print("=" * 80)
        print(f"📊 Prompt Length: {len(full_prompt)} characters")
        print(f"📊 Template Length: {len(template_content.template)} characters")
        print("=" * 80)
    else:
        # Always show basic info
        print(f"📝 Query: {query}")
        print(f"📊 Template Length: {len(template_content.template)} characters")
        print(f"📊 Context Length: {len(str(contexts))} characters")
        print(f"📊 History Length: {len(str(history_context))} characters")

    chain = (
            prompt | environment.get_llm(model=constant.MODEL_CHATBOT_CUSTOM_PROMPT) | StrOutputParser()
    )

    answer = ""

    async def generate_chat_responses(message):
        nonlocal answer
        stop_yielding = False

        ans_ref = ""
        buffer = ""

        # Lưu lịch sử: khởi tạo hội thoại và ghi message của user
        try:
            db = await get_mongodb_manager()
            await db.create_conversation(str(session_id), str(user_id), {
                "role": "user",
                "content": str(query),
                "metadata": {"collections": collections}
            }, metadata={"history_id": str(history_id)})
        except Exception as db_err:
            print(f"[History] create_conversation error: {db_err}")

        async for chunk in chain.astream(message):
            if "📑" in chunk:
                stop_yielding = True

            if " - " not in chunk and (" -" in chunk or "- " in chunk):
                chunk = " " + chunk

            if not stop_yielding:
                # Bỏ qua chunk rỗng/space-only để tránh sự kiện trống
                if chunk and chunk.strip() != "":
                    # Gom chunk để tránh gửi ký tự lẻ
                    buffer += chunk
                    should_flush = (
                        buffer.endswith((" ", ".", ",", "!", "?", "\n"))
                        or len(buffer) >= 32
                    )
                    if should_flush:
                        answer += buffer
                        try:
                            sse_payload = json.dumps({"content": buffer}, ensure_ascii=False)
                        except Exception:
                            sse_payload = json.dumps({"content": str(buffer)})
                        yield f"data: {sse_payload}\r\n\r\n"
                        buffer = ""
            else:
                ans_ref += chunk

        # Flush phần buffer còn lại nếu có
        if buffer:
            answer += buffer
            try:
                sse_payload_tail = json.dumps({"content": buffer}, ensure_ascii=False)
            except Exception:
                sse_payload_tail = json.dumps({"content": str(buffer)})
            yield f"data: {sse_payload_tail}\r\n\r\n"

        pages = reference.extract_reference_document_numbers(ans_ref)
        print("pages: ", pages)

        filter_references = reference.filter_reference_from_page(references, pages)

        # Gửi metadata tham chiếu theo chuẩn SSE
        try:
            meta_payload = json.dumps({"metadata": {"reference": filter_references}}, ensure_ascii=False)
        except Exception:
            meta_payload = json.dumps({"metadata": {"reference": []}})
        yield f"data: {meta_payload}\r\n\r\n"

        # Kết thúc stream theo chuẩn SSE
        yield "data: [DONE]\r\n\r\n"

        answer = clean.clean_special_characters(answer)

        # Ghi message assistant vào histories
        try:
            db = await get_mongodb_manager()
            await db.append_message(str(session_id), {
                "role": "assistant",
                "content": str(answer),
                "metadata": {"reference": filter_references}
            })
        except Exception as db_err2:
            print(f"[History] append_message error: {db_err2}")

        threading.Thread(
            target=_history.save_history,
            args=(user_id, history_id, session_id, query, answer, "", "", references, ""),
        ).start()

        num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_CHATBOT_CUSTOM_PROMPT, name="chatbot_custom_prompt")
        response_time = time.time() - start_time

        threading.Thread(
            target=_token.save_tokens,
            args=(user_id, "Response", num_token_input, num_tokens_output, constant.MODEL_CHATBOT_CUSTOM_PROMPT, round(response_time, 2)),
        ).start()

        return

    return generate_chat_responses({
        "system": str(system_prompt),
        "template": str(template_content.template),
        "checklist": str(checklist.checklist),
        "question": str(query),
        "context": str(contexts),
        "history": str(history_context),
        "time_now": str(current_time),
        "text": str(product_context),
        "system_instruction_user": str(system_instruction_user),
        "message_payload": message_payload,
    })
    # return generate_chat_responses(message_payload)


def chatbot_custom_prompt(user_id, query, collections, session_id, history_id, system_instruction_user: str = "", include_products: bool = True):
    """
    Phiên bản không streaming của chatbot custom prompt với hỗ trợ dữ liệu sản phẩm.
    """
    start_time = time.time()

    retrievers, references = retriever.get_retriever_reference_qdrant(collections, query, k=constant.K_CHATBOT_CUSTOM_PROMPT)

    contexts = clean.clean_special_characters(retrievers)

    # Lấy thông tin sản phẩm nếu được yêu cầu
    product_context = "Không có thông tin sản phẩm"  # Giá trị mặc định
    if include_products:
        try:
            # Tạo event loop mới cho async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Kiểm tra xem có tên sản phẩm trong query không
            product_names = extract_product_names_from_query(query)
            
            if product_names:
                print(f"🔍 Phát hiện tên sản phẩm trong query: {product_names}")
                # Nếu có tên sản phẩm, tìm kiếm trong Qdrant
                qdrant_results = loop.run_until_complete(search_products_qdrant(query))
                if qdrant_results:
                    product_context = qdrant_results
                    print(f"✅ Tìm thấy {len(qdrant_results.split('---')) - 1} sản phẩm từ Qdrant")
                else:
                    # Nếu không tìm thấy trong Qdrant, thử tìm trong MongoDB
                    product_context = loop.run_until_complete(get_product_context(query))
                    print("✅ Tìm kiếm trong MongoDB")
            else:
                # Không phát hiện tên sản phẩm, tìm kiếm thông thường trong MongoDB
                product_context = loop.run_until_complete(get_product_context(query))
                print("🔍 Không phát hiện tên sản phẩm, tìm kiếm trong MongoDB")
            
            loop.close()
            
            # Không thêm product_context vào contexts nữa vì nó được truyền riêng như biến text
            # if product_context:
            #     contexts = f"{contexts}\n{product_context}"
                
        except Exception as e:
            print(f"Lỗi khi lấy thông tin sản phẩm: {e}")
            # Tiếp tục mà không có product context nếu có lỗi

    if session_id == "":
        session_id = str(uuid.uuid4())

    history_context = _history.get_history_context(user_id, query, session_id)

    current_time = time_utils.get_current_vn_time()

    contexts, num_token_input = context_reduce.context_reduce(contexts, constant.MODEL_CHATBOT_CUSTOM_PROMPT)

    # Lấy system prompt từ file system.py và làm sạch
    system_prompt = clean.clean_special_characters(system.system)
    # Làm sạch system_instruction_user do người dùng nhập
    system_instruction_user = clean.clean_special_characters(str(system_instruction_user or ""))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_chatbot_custom.CHATBOT),
        ]
    )

    chain = (
            prompt | environment.get_llm(model=constant.MODEL_CHATBOT_CUSTOM_PROMPT) | StrOutputParser()
    )

    answer = chain.invoke({
        "system": str(system_prompt),
        "template": str(template_content.template),
        "checklist": str(checklist.checklist),
        "question": str(query),
        "context": str(contexts),
        "history": str(history_context),
        "time_now": str(current_time),
        "text": str(product_context),
        "system_instruction_user": str(system_instruction_user),
    })

    pages = reference.extract_reference_document_numbers(answer)
    filter_references = reference.filter_reference_from_page(references, pages)

    answer = clean.clean_special_characters(answer)

    threading.Thread(
        target=_history.save_history,
        args=(user_id, history_id, session_id, query, answer, "", "", references, ""),
    ).start()

    # Lưu lịch sử vào MongoDB (non-stream)
    try:
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)
        db = loop2.run_until_complete(get_mongodb_manager())
        loop2.run_until_complete(db.create_conversation(str(session_id), str(user_id), {
            "role": "user",
            "content": str(query),
            "metadata": {"collections": collections}
        }, metadata={"history_id": str(history_id)}))
        loop2.run_until_complete(db.append_message(str(session_id), {
            "role": "assistant",
            "content": str(answer),
            "metadata": {"reference": filter_references}
        }))
        loop2.close()
    except Exception as db_err3:
        print(f"[History] non-stream write error: {db_err3}")

    num_tokens_output = _token.calculate_tokens(answer, model=constant.MODEL_CHATBOT_CUSTOM_PROMPT, name="chatbot_custom_prompt")
    response_time = time.time() - start_time

    threading.Thread(
        target=_token.save_tokens,
        args=(user_id, "Response", num_token_input, num_tokens_output, constant.MODEL_CHATBOT_CUSTOM_PROMPT, round(response_time, 2)),
    ).start()

    return answer, filter_references

