from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import asyncio
import re
import uuid
import base64
from typing import Union, List, Dict, Any, Optional

from bot.v1 import bot_suggestion, chatbot_custom_prompt
from controllers.databases.nosql.mongodb import get_mongodb_manager
from api.image import _analyze_image_bytes

router = APIRouter()


def extract_keywords_vi(text: str) -> str:
    """Chuẩn hóa và trích từ khóa tiếng Việt phục vụ truy xuất sản phẩm.

    - Lowercase, bỏ ký tự thừa
    - Loại bỏ từ dừng (có, không, v.v.) và danh từ chung không cần thiết
    - Loại bỏ trùng lặp, giữ nguyên thứ tự
    """
    if text is None:
        return ""
    s = str(text).lower()
    s = re.sub(r"[\-_/]+", " ", s)
    s = re.sub(r"[^\w\sÀ-ỹ]", " ", s, flags=re.UNICODE)
    tokens = [t.strip() for t in s.split() if t.strip()]

    stopwords = {
        "có", "không", "ko", "k", "như", "nào", "hả", "vậy", "à", "ạ",
        "là", "thì", "và", "hoặc", "một", "cái", "chiếc", "loại",
        "sản", "phẩm", "xin", "hỏi", "giúp", "với", "giùm",
        # danh từ chung theo domain (giữ tập trung vào model/color)
        "túi", "xách", "ví", "giày", "dép"
    }

    seen = set()
    result = []
    for t in tokens:
        if t in stopwords:
            continue
        if t in seen:
            continue
        seen.add(t)
        result.append(t)

    return " ".join(result)


class ChatbotRequest(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    collections: Union[str, int, List[Any], Dict[str, Any]] = []
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""


class ChatbotCustomPromptRequest(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    collections: Union[str, int, List[Any], Dict[str, Any]] = []
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    system_instruction_user: Union[str, int, List[Any], Dict[str, Any]] = ""
    include_products: bool = True
    image_text: Union[str, int, List[Any], Dict[str, Any]] = ""


class ChartRequest(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    context: Union[str, int, List[Any], Dict[str, Any]] = ""


class SuggestRequest(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    answer: Union[str, int, List[Any], Dict[str, Any]] = ""
    context: Union[str, int, List[Any], Dict[str, Any]] = ""


class AgentProvinceMerger(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    
    
class AgentKAT(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    prompt: Union[str, int, List[Any], Dict[str, Any]] = ""


class ProductSearchRequest(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    query: Union[str, int, List[Any], Dict[str, Any]] = ""
    limit: Union[str, int, List[Any], Dict[str, Any]] = 5


    
    
# ===================================================================================
# BASIC
@router.post("/v1/chatbot-basic")
@router.post("/v1/chatbot-basic/")
async def chatbot_basic_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            chatbot_basic.chatbot_basic,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        content = {"status": 200, "message": "success", "data": answer}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chatbot-basic-stream")
@router.post("/v1/chatbot-basic-stream/")
async def chatbot_basic_stream_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            chatbot_basic.chatbot_basic_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# PRODUCT SEARCH FROM QDRANT
@router.post("/v1/search-products-qdrant")
@router.post("/v1/search-products-qdrant/")
async def search_products_qdrant_endpoint(request: ProductSearchRequest):
    try:
        from controllers.databases.vector.qdrant.qdrant import similarity_search_qdrant_data_with_score
        from langchain_community.vectorstores import Qdrant
        from qdrant_client import QdrantClient
        from configs import environment, constant
        
        # Khởi tạo Qdrant client và vectorstore cho collection 'kat_products'
        client = QdrantClient(
            url=constant.QDRANT_SERVER,
            api_key=constant.QDRANT_API_KEY if constant.QDRANT_API_KEY else None,
            timeout=30,
        )

        # Kiểm tra collection tồn tại
        if not client.collection_exists("kat_products"):
            content = {"status": 404, "message": "kat_products collection not found"}
            return JSONResponse(content=jsonable_encoder(content), status_code=404)

        # Tạo vectorstore từ client (tránh lỗi from_existing_collection signature)
        qdrant_vectorstore = Qdrant(
            client=client,
            collection_name="kat_products",
            embeddings=environment.embeddings_model,
            content_payload_key="text",
        )
        
        # Search for products
        limit = int(request.limit) if isinstance(request.limit, (str, int)) else 5
        query_text = extract_keywords_vi(str(request.query))
        search_results = similarity_search_qdrant_data_with_score(
            qdrant_vectorstore,
            query_text if query_text else str(request.query),
            k=limit,
        )
        
        # Format results
        products = []
        for doc, score in search_results:
            product_info = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            products.append(product_info)
        
        content = {"status": 200, "message": "success", "data": products}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# REFERENCE
@router.post("/v1/chatbot-reference")
@router.post("/v1/chatbot-reference/")
async def chatbot_reference_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer, references = await loop.run_in_executor(
            None,
            chatbot_reference.chatbot_reference,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        content = {"status": 200, "message": "success", "data": {"answer": answer, "reference": references}}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chatbot-reference-stream")
@router.post("/v1/chatbot-reference-stream/")
async def chatbot_reference_stream_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            chatbot_reference.chatbot_reference_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# CHART
@router.post("/v1/chatbot-chart")
@router.post("/v1/chatbot-chart/")
async def chatbot_chart_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer, references = await loop.run_in_executor(
            None,
            chatbot_chart.chatbot_chart,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        content = {"status": 200, "message": "success", "data": {"answer": answer, "reference": references}}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chatbot-chart-stream")
@router.post("/v1/chatbot-chart-stream/")
async def chatbot_chart_stream_endpoint(request: ChatbotRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            chatbot_chart.chatbot_chart_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chart")
@router.post("/v1/chart/")
async def get_chart_endpoint(request: ChartRequest):
    try:
        loop = asyncio.get_event_loop()

        answer = await loop.run_in_executor(
            None,
            chatbot_chart.get_chart,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.context,
        )

        content = {"status": 200, "message": "success", "data": answer}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# SUGGESTION
@router.post("/v1/suggestions")
@router.post("/v1/suggestions/")
async def get_suggestions_endpoint(request: SuggestRequest):
    try:
        loop = asyncio.get_event_loop()

        answer = await loop.run_in_executor(
            None,
            bot_suggestion.chatbot_suggestion,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.answer,
            request.context,
        )

        content = {"status": 200, "message": "success", "data": answer}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# CUSTOM PROMPT
@router.post("/v1/chatbot-custom-prompt")
@router.post("/v1/chatbot-custom-prompt/")
async def chatbot_custom_prompt_endpoint(request: ChatbotCustomPromptRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id, f"include_products={request.include_products}")

        answer, references = await loop.run_in_executor(
            None,
            chatbot_custom_prompt.chatbot_custom_prompt,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
            request.system_instruction_user,
            request.include_products,
            str(request.image_text or ""),
        )

        content = {"status": 200, "message": "success", "data": {"answer": answer, "reference": references}}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chatbot-custom-prompt-stream")
@router.post("/v1/chatbot-custom-prompt-stream/")
async def chatbot_custom_prompt_stream_endpoint(request: ChatbotCustomPromptRequest):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.collections, request.session_id, request.history_id, f"include_products={request.include_products}")

        answer = await loop.run_in_executor(
            None,
            chatbot_custom_prompt.chatbot_custom_prompt_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.collections,
            request.session_id,
            request.history_id,
            request.system_instruction_user,
            request.include_products,
            str(request.image_text or ""),
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/chatbot-with-image")
@router.post("/v1/chatbot-with-image/")
async def chatbot_with_image_endpoint(
    user_id: str = Form(...),
    query: str = Form(...),
    collections: str = Form("[]"),
    session_id: str = Form(""),
    history_id: str = Form(""),
    system_instruction_user: str = Form(""),
    include_products: bool = Form(True),
    image: UploadFile = File(...)
):
    """
    Chatbot endpoint với hỗ trợ upload ảnh.
    Ảnh sẽ được phân tích và kết quả được thêm vào prompt.
    """
    try:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # Read image data
        image_bytes = await image.read()
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Kích thước ảnh không được vượt quá 10MB")
        
        # Analyze image
        image_analysis = await _analyze_image_bytes(image_bytes, image.content_type)
        
        # Store image in MongoDB
        db = await get_mongodb_manager()
        image_id = str(uuid.uuid4())
        
        # Save image to MongoDB
        image_doc_id = await db.save_image(
            image_id=image_id,
            user_id=user_id,
            image_data=image_bytes,
            content_type=image.content_type,
            metadata={
                "filename": image.filename,
                "size": len(image_bytes),
                "query": query
            }
        )
        
        if not image_doc_id:
            print("Cảnh báo: Không thể lưu ảnh vào MongoDB")
        
        # Combine query with image analysis
        enhanced_query = f"{query}\n\n[Phân tích ảnh]: {image_analysis}"
        
        # Process with chatbot
        loop = asyncio.get_event_loop()
        
        print(f"User: {user_id}, Query: {enhanced_query}, Collections: {collections}")
        
        answer, references = await loop.run_in_executor(
            None,
            chatbot_custom_prompt.chatbot_custom_prompt,
            re.sub(r"\s+", "", user_id),
            enhanced_query,
            collections,
            session_id,
            history_id,
            system_instruction_user,
            include_products,
            "",  # image_text is empty since we processed the image
        )
        
        # Return response with image reference
        content = {
            "status": 200, 
            "message": "success", 
            "data": {
                "answer": answer, 
                "reference": references,
                "image_id": image_id if image_doc_id else None,
                "image_analysis": image_analysis
            }
        }
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# ===================================================================================
# AGENT PROVINCE MERGER
@router.post("/v1/agent-province-merger")
@router.post("/v1/agent-province-merger/")
async def agent_province_merger_endpoint(request: AgentProvinceMerger):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            agent_province_merger.agent_province_merger,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.session_id,
            request.history_id,
        )

        content = {"status": 200, "message": "success", "data": answer}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/agent-province-merger-stream")
@router.post("/v1/agent-province-merger-stream/")
async def agent_province_merger_stream_endpoint(request: AgentProvinceMerger):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.session_id, request.history_id)

        answer = await loop.run_in_executor(
            None,
            agent_province_merger.agent_province_merger_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.session_id,
            request.history_id,
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/agent-kat-stream")
@router.post("/v1/agent-kat-stream/")
async def agent_kat_stream_endpoint(request: AgentKAT):
    try:
        loop = asyncio.get_event_loop()

        print(re.sub(r"\s+", "", request.user_id), request.query, request.session_id, request.history_id, request.prompt)

        answer = await loop.run_in_executor(
            None,
            agent_kat.agent_kat_stream,
            re.sub(r"\s+", "", request.user_id),
            request.query,
            request.session_id,
            request.history_id,
            request.prompt,
        )

        return StreamingResponse(
            answer,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


