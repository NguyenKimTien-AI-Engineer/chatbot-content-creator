
import streamlit as st
import asyncio
import random
import string
import httpx
import json
import pandas as pd
import requests
import ast
from bs4 import BeautifulSoup


from configs import constant

url_read_collections_user = f"{constant.SERVER_ADDRESS}/api/v1/qdrant/collections/user"
url_read_all_collections = f"{constant.SERVER_ADDRESS}/api/v1/qdrant/collections/all"
 

url_chat_custom_prompt_stream = f"{constant.SERVER_ADDRESS}/api/v1/chatbot-custom-prompt-stream"

url_chart_stream = f"{constant.SERVER_ADDRESS}/api/v1/chatbot-chart-stream"
url_write_chart = f"{constant.SERVER_ADDRESS}/api/v1/chart"

timeout = 30000.0
size_chart = 600


async def api_get_collections_user(user_id):
    try:
        url = f"{url_read_collections_user}/{user_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("data", "")
            return data
        else:
            return []

    except Exception as e:
        print(f"An error api_get_year: {str(e)}")
        return []


async def api_get_all_collections():
    try:
        response = requests.get(url_read_all_collections)

        if response.status_code == 200:
            data = response.json().get("data", "")
            return data
        else:
            return []

    except Exception as e:
        print(f"An error api_get_year: {str(e)}")
        return []


async def call_chatbot_api(user_id, query, collections, session_id, history_id, chatbot_type):
    # Use custom prompt endpoint by default, fallback to standard endpoints
    if chatbot_type == "chart":
        url = url_chart_stream
        payload = {
            "user_id": user_id,
            "query": query,
            "collections": collections,
            "session_id": session_id,
            "history_id": history_id,
        }
    else:
        # Use custom prompt endpoint for default chatbot mode
        url = url_chat_custom_prompt_stream
        payload = {
            "user_id": user_id,
            "query": query,
            "collections": collections,
            "session_id": session_id,
            "history_id": history_id,
            "include_products": True,  # Enable product information
        }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    print(f"Stream text in UI Error: {response.text}")
                    return

                async for chunk in response.aiter_text():
                    yield chunk

    except Exception as e:
        print(f"Error in call_chatbot_api: {str(e)}")
        pass


async def write_chart(user_id, query, context):
    try:
        data = {
            "user_id": user_id,
            "query": query,
            "context": context
        }
        # Gửi dữ liệu dưới dạng JSON
        response = requests.post(url_write_chart, json=data, timeout=timeout)

        if response.status_code == 200:
            _chart = response.json().get("data", None)

            if _chart is not None:
                st.components.v1.html(_chart, height=size_chart)
                st.session_state.messages.append({"role": "chart", "content": _chart})

        else:
            error_message = response.json().get("message", "Unknown error.")
            print(f"Lỗi khi vẽ biểu đồ: {error_message}")

    except Exception as e:
        print(f"Error: {str(e)}")


def remove_duplicate_p_tag(text):
    soup = BeautifulSoup(text, "html.parser")

    p_tag = soup.find("p")
    if p_tag:
        p_content = p_tag.get_text(strip=True)

        p_tag.extract()

        for br in soup.find_all("br"):
            br.extract()

        remaining_text = soup.get_text(strip=True)

        if p_content == remaining_text:
            return remaining_text

    text = text.replace("##### ####", "#####").replace("#### ####", "####").replace("### ####", "###")

    return text


async def chat_stream(user_id, query, collections, session_id, history_id, chatbot_type):
    full_answer = ""

    try:
        with st.spinner("Đang suy nghĩ..."):
            placeholder = st.empty()
            full_answer = ""

            buffer_tmp = []
            buffer_tmp_check = False

            async for message in call_chatbot_api(user_id, query, collections, session_id, history_id, chatbot_type):
                if message:
                    if buffer_tmp_check or message.strip().startswith('{"metadata"'):
                        buffer_tmp_check = True
                        buffer_tmp.append(message)

                    else:
                        if message == "### === GENERATE CHART === ###":
                            full_answer_ = f"{full_answer}\n\nBiểu đồ đang được tạo. Vui lòng đợi trong giây lát..."
                            placeholder.markdown(full_answer_, unsafe_allow_html=True)

                            with st.spinner("Đang tạo biểu đồ..."):
                                await asyncio.sleep(10)

                        else:
                            full_answer += message
                            placeholder.markdown(full_answer, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_answer})
            st.session_state.last_answer = full_answer

            if buffer_tmp:
                try:
                    combined_message = ''.join(buffer_tmp)

                    data = json.loads(combined_message)

                    metadata_array = data.get("metadata", None)
                    if metadata_array is not None:
                        reference = metadata_array.get("reference", None)
                        if reference is not None:
                            st.session_state.messages.append({"role": "reference", "content": reference})

                        chart = metadata_array.get("chart", None)
                        if chart is not None:
                            st.session_state.messages.append({"role": "chart", "content": chart})

                except json.JSONDecodeError as e:
                    print(f"Error parsing metadata: {str(e)}")

                    pass

        st.markdown("")
        return full_answer
    except Exception as e:
        print(f"An error occurred chat_with_files_separated_stream: {str(e)}")

        return full_answer


def generate_random_history_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))


def fix_links_in_html(raw_html: str) -> str:
    """
    Tìm tất cả các thẻ <group-link> và biến chúng thành một icon.
    Khi bấm icon, sẽ hiển thị danh sách liên kết bên trong.
    """

    soup = BeautifulSoup(raw_html, "html.parser")

    for group_link in soup.find_all("group-link"):
        links = group_link.find_all("a")
        details_tag = soup.new_tag("details")
        summary_tag = soup.new_tag("summary")

        icon_html = """📑"""
        summary_tag.append(BeautifulSoup(icon_html, "html.parser"))

        content_div = soup.new_tag("div")

        ul_tag = soup.new_tag("ul")
        ul_tag["style"] = "list-style-type: none; padding-top: 7px; padding-bottom: 5px; margin: 10px 0; background-color: #f7f7f7; border-radius: 5px;"  # Loại bỏ dấu đầu dòng, thêm khoảng cách

        for link in links:
            li_tag = soup.new_tag("li")
            li_tag["style"] = "margin-bottom: 5px;"

            new_a = soup.new_tag("a", href=link.get("href"), target="_blank")
            new_a.string = link.get_text(strip=True)
            new_a["style"] = "text-decoration: none; color: #0068c9;"

            li_tag.append(new_a)
            ul_tag.append(li_tag)

        content_div.append(ul_tag)
        details_tag.append(summary_tag)
        details_tag.append(content_div)

        group_link.replace_with(details_tag)

    return str(soup)


def main():
    st.set_page_config(
        page_title="MekongAI Bot",
        page_icon="https://mekongai.net/_next/static/media/favicon.76f5f210.ico",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.session_state.setdefault("uploaded_file", None)
    st.session_state.setdefault("file_content", "")

    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", "")
    st.session_state.setdefault("metadata", [])
    st.session_state.setdefault("reference", [])
    st.session_state.setdefault("last_answer", "")
    st.session_state.setdefault("chart", [])

    # st.session_state.setdefault("ref_toggle", True)
    st.session_state.setdefault("ref_toggle", False)
    st.session_state.setdefault("prompt_toggle", False)

    # Set default to custom prompt mode
    # st.session_state.prompt_toggle = True

    # st.session_state.setdefault("prompt", "")
    st.session_state.prompt_toggle = False

    st.session_state.setdefault("is_typing", False)

    st.session_state.setdefault("user_id", "")
    # Loại bỏ trạng thái liên quan đến gợi ý câu hỏi và chọn/tải sản phẩm

    # Predefined Qdrant collection for non-custom mode
    st.session_state.setdefault("default_collection", "CHATBOT_MekongAI_d41b1532-bf75-481d-ad6d-b7dac8cbae4d")

    if st.session_state.session_id == "":
        session_id = generate_random_history_id()
        st.session_state.session_id = session_id

    # Hiển thị nội dung chat trước đó
    for message in st.session_state.messages:
        icon = "./resources/icon/user.png" if message["role"] == "user" else "./resources/icon/bot.png"

        if message["role"] == "assistant" and message["content"]:
            with st.chat_message("assistant", avatar=icon):
                content = message["content"]
                st.markdown(content, unsafe_allow_html=True)

        elif message["role"] == "chart" and message["content"]:
            with st.chat_message("assistant", avatar="📈"):
                st.components.v1.html(message["content"], height=size_chart)

        elif message["role"] == "reference" and message["content"]:
            if st.session_state.ref_toggle:
                with st.chat_message("assistant", avatar="📑"):
                    for metadata in message["content"]:
                        with st.expander(metadata['title']):
                            content = metadata['content']

                            # chỉ xử lý khi content là str
                            if isinstance(content, str):
                                parsed = None

                                # 1. Thử JSON
                                try:
                                    parsed = json.loads(content)
                                except json.JSONDecodeError:
                                    pass
                                else:
                                    # json.loads thành công
                                    if isinstance(parsed, (dict, list)):
                                        st.json(parsed)
                                        continue  # quay vòng expander tiếp

                                # 2. Thử ast.literal_eval
                                try:
                                    # trước đó bạn đã replace newline và bracket nếu cần
                                    single_line = content.replace("\n", "\\n")
                                    cleaned = single_line.replace("\\[", "[").replace("\\]", "]")
                                    parsed = ast.literal_eval(cleaned)
                                except Exception:
                                    parsed = None

                                if isinstance(parsed, (dict, list)):
                                    st.json(parsed)
                                    continue

                                # 3. Không parse được JSON/literal -> coi như text
                                raw = content.replace("\n", "\n\n")
                                st.markdown(fix_links_in_html(raw), unsafe_allow_html=True)
                                continue

                            # nếu content vốn đã là dict hoặc list
                            if isinstance(content, dict):
                                st.json(content)
                            elif isinstance(content, list):
                                # xử lý bảng list of lists
                                if content and all(isinstance(r, (list, tuple)) for r in content):
                                    headers, rows = content[0], content[1:]
                                    df = pd.DataFrame(rows, columns=headers)
                                    st.table(df)
                                else:
                                    st.json(content)
                            else:
                                st.markdown(str(content))

        elif message["content"]:
            with st.chat_message(message["role"], avatar=icon):
                st.write(message["content"])

    # Add custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Enhanced chat input styling */
    .stChatInput {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stChatInput:focus {
        border-color: #2196f3;
        box-shadow: 0 4px 16px rgba(33, 150, 243, 0.2);
        outline: none;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Expander styling */
    .stExpander {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        background: #fafafa;
    }
    .stExpander:hover {
        border-color: #2196f3;
    }
    
    /* Responsive styles */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 14px;
            height: 2.5em;
        }
    }
    
    /* Loading spinner */
    .stSpinner > div {
        text-align: center;
        color: #2196f3;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Giao diện nhập chat
    # Chat input
    query = st.chat_input(placeholder="Nhập câu hỏi...")
    
    if query:
        # Use predefined collection for non-custom mode
        collections = [st.session_state.default_collection]
        send_message(st.session_state.user_id, query, collections, st.session_state.session_id, "")


def send_message(user_id, query, collections, session_id, history_id):
    if query:
        st.session_state.messages.append({"role": "user", "content": query, "type": "text"})
        with st.chat_message("user", avatar="./resources/icon/user.png"):
            st.write(query)

        with st.chat_message("assistant", avatar="./resources/icon/bot.png"):
            st.session_state.is_typing = True
            query_lower = query.lower()
            
            # Determine chatbot type based on query content
            chatbot_type = "reference"  # Default to reference mode for non-custom chatbot
            
            # Check if query contains chart/chart-related keywords
            if "phân tích" in query_lower or "so sánh" in query_lower or "phân loại" in query_lower or "thống kê" in query_lower or "biểu đồ" in query_lower or "vẽ" in query_lower or "chart" in query_lower or "draw" in query_lower:
                chatbot_type = "chart"

            # Use predefined collection if no collections are provided
            if not collections:
                collections = [st.session_state.default_collection]

            answer = asyncio.run(chat_stream(user_id, query, collections, session_id, history_id, chatbot_type))
            if chatbot_type == "chart":
                with st.spinner("Đang vẽ biểu đồ..."):
                    asyncio.run(write_chart(user_id, query, answer))

            st.session_state.is_typing = False
            st.rerun()