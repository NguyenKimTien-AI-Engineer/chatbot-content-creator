from langchain_core.documents import Document
from typing import List, Tuple
from bs4 import BeautifulSoup
import uuid
import re

from configs import constant
from controllers.data import clean


def node_structured_pdf(
        doc_contents,
        page_image_base64_list,
        file_name
) -> tuple[list[Document], list[str]]:
    docs = []
    doc_ids = []

    print("Docs length: ", len(doc_contents))
    print("Image length: ", len(page_image_base64_list))

    # Xác định loại dữ liệu trước khi xử lý
    data_type = detect_data_type(doc_contents)
    print(f"Detected data type: {data_type}")

    if data_type == "table_format":
        # Xử lý format table (type 1 cũ)
        try:
            # Kiểm tra đồng bộ giữa doc_contents và page_image_base64_list
            max_page = max([content["page"] for content in doc_contents])  # Tìm trang lớn nhất
            all_pages = list(range(1, max_page + 1))  # Danh sách tất cả các trang
            existing_pages = [content["page"] for content in doc_contents]  # Danh sách trang hiện có
            missing_pages = set(all_pages) - set(existing_pages)  # Trang bị thiếu

            # Thêm các trang bị thiếu với nội dung rỗng
            for missing_page in missing_pages:
                doc_contents.append({
                    "page": missing_page,
                    "data": None
                })

            # Sắp xếp lại theo thứ tự trang
            doc_contents.sort(key=lambda x: x["page"])

            # Lưu thông tin nhỏ về các trang
            for content in doc_contents:
                try:
                    page = content["page"]

                    # Đảm bảo rằng `page` là số nguyên
                    if not isinstance(page, int):
                        page = int(page)

                    # Kiểm tra nếu `data` tồn tại
                    if content["data"] is not None:
                        df = content["data"]
                        html_content = df.to_html(index=False)
                    else:
                        html_content = ""  # Trang trống

                except Exception as e:
                    print("Error processing table format: ", e)
                    html_content = ""
                    page = content.get("page", -1)

                # Kiểm tra danh sách trước khi truy cập chỉ số
                try:
                    page_image_base64 = page_image_base64_list[int(page) - 1] if 0 < page <= len(page_image_base64_list) else ""
                except Exception as e:
                    print("Error with page_image_base64 access: ", e)
                    page_image_base64 = ""

                # Cắt nội dung thành các đoạn chunk size
                content_chunks = split_content_by_approx_words(html_content, constant.NODE_CHUNK_SIZE_TYPE_1)
                hierarchy = f"{file_name} -> Page {page}"

                for chunk in content_chunks:
                    _id = str(uuid.uuid4())
                    metadata = {
                        "doc_id": _id,
                        "summary": "",
                        "page_content": html_content,
                        "hierarchy": hierarchy,
                        "page": page,
                        "file_name": file_name,
                        "page_image_base64": page_image_base64,
                    }
                    docs.append(Document(page_content=chunk.lower(), metadata=metadata))
                    doc_ids.append(_id)

                _id = str(uuid.uuid4())
                metadata = {
                    "doc_id": _id,
                    "summary": "",
                    "page_content": html_content,
                    "hierarchy": hierarchy,
                    "page": page,
                    "file_name": file_name,
                    "page_image_base64": page_image_base64,
                }
                docs.append(Document(page_content=html_content.lower(), metadata=metadata))
                doc_ids.append(_id)

        except Exception as e:
            print("Error processing table format: ", e)

    else:
        # Xử lý format element (type 2 cũ) - Mixed format từ process_pdf
        try:
            max_page = len(doc_contents)  # Tổng số trang

            for i in range(max_page):
                if i < len(doc_contents):
                    page_elements = doc_contents[i]
                    content_string = ""
                    
                    for element in page_elements:
                        try:
                            # Xử lý các loại element khác nhau
                            if isinstance(element, dict):
                                # Đây là table element từ extract_table_pdf
                                if element.get("type") == "table" and "data" in element:
                                    # Chuyển DataFrame thành HTML
                                    df = element["data"]
                                    table_html = df.to_html(index=False)
                                    content_string += table_html + "\n"
                                else:
                                    # Dict khác, lấy text nếu có
                                    element_text = element.get("text", "")
                                    if element_text.strip():
                                        content_string += element_text + "\n"
                            elif hasattr(element, 'text'):
                                # Element từ unstructured hoặc OCR
                                if element.text.strip():
                                    content_string += element.text + "\n"
                            elif isinstance(element, str):
                                # String thuần túy
                                if element.strip():
                                    content_string += element + "\n"
                            else:
                                # Fallback: convert to string
                                element_str = str(element)
                                if element_str.strip():
                                    content_string += element_str + "\n"
                        except Exception as element_error:
                            print(f"Error processing element: {element_error}")
                            continue
                else:
                    # Nếu thiếu trang, thêm nội dung trống
                    content_string = ""

                hierarchy = f"{file_name} -> Page {i + 1}"

                # Chỉ tạo chunks nếu có nội dung
                if content_string.strip():
                    content_chunks = split_content_by_approx_words(content_string, constant.NODE_CHUNK_SIZE_TYPE_1)
                else:
                    content_chunks = [""]  # Trang trống

                try:
                    page_image_base64 = page_image_base64_list[i] if i < len(page_image_base64_list) else ""
                except Exception as e:
                    print("Error with page_image_base64 access: ", e)
                    page_image_base64 = ""

                for chunk in content_chunks:
                    if not chunk.strip():  # Skip empty chunks
                        continue
                        
                    _id = str(uuid.uuid4())
                    metadata = {
                        "doc_id": _id,
                        "summary": "",
                        "page_content": content_string,
                        "hierarchy": hierarchy,
                        "page": i + 1,
                        "file_name": file_name,
                        "page_image_base64": page_image_base64,
                    }
                    docs.append(Document(page_content=chunk.lower(), metadata=metadata))
                    doc_ids.append(_id)

                # Luôn tạo một document chính cho trang (ngay cả khi trống)
                _id = str(uuid.uuid4())
                metadata = {
                    "doc_id": _id,
                    "summary": "",
                    "page_content": content_string,
                    "hierarchy": hierarchy,
                    "page": i + 1,
                    "file_name": file_name,
                    "page_image_base64": page_image_base64,
                }
                docs.append(Document(page_content=content_string.lower(), metadata=metadata))
                doc_ids.append(_id)

        except Exception as e:
            print("Error processing element format: ", e)

    return docs, doc_ids


def detect_data_type(doc_contents):
    """
    Xác định loại dữ liệu để chọn phương pháp xử lý phù hợp
    Returns:
    - 'table_format': Dữ liệu theo format table cũ (có key "page", "data")
    - 'element_format': Dữ liệu theo format element mới (list of elements per page)
    """
    try:
        if not doc_contents or len(doc_contents) == 0:
            return 'element_format'
        
        # Kiểm tra phần tử đầu tiên
        first_item = doc_contents[0]
        
        # Nếu là dict có key "page" và "data" -> table format
        if isinstance(first_item, dict) and "page" in first_item and "data" in first_item:
            return 'table_format'
        
        # Nếu là list (mỗi page là một list elements) -> element format
        elif isinstance(first_item, list):
            return 'element_format'
        
        # Default fallback
        else:
            return 'element_format'
            
    except Exception as e:
        print(f"Error detecting data type: {e}")
        return 'element_format'  # Default fallback


def node_structured_docx(
        doc_contents,
        page_image_base64_list,
        file_name,
) -> tuple[list[Document], list[str]]:
    docs = []
    doc_ids = []

    try:
        max_page = len(doc_contents)

        for i in range(max_page):
            content = ""

            if i < len(doc_contents):
                content = doc_contents[i]

                if content == "":
                    continue

            hierarchy = f"{file_name} -> Page {i + 1}"

            content_chunks = split_content_by_approx_words(content, constant.NODE_CHUNK_SIZE_TYPE_1)

            try:
                page_image_base64 = page_image_base64_list[i]
            except Exception as e:
                print("Error with page_image_base64 access: ", e)
                page_image_base64 = ""

            for chunk in content_chunks:
                _id = str(uuid.uuid4())
                metadata = {
                    "doc_id": _id,
                    "summary": "",
                    "page_content": content,
                    "hierarchy": hierarchy,
                    "page": i + 1,
                    "file_name": file_name,
                    "page_image_base64": page_image_base64,
                }
                # Tạo document với từng chunk đã chia
                docs.append(Document(page_content=chunk.lower(), metadata=metadata))
                doc_ids.append(_id)

            _id = str(uuid.uuid4())
            metadata = {
                "doc_id": _id,
                "summary": "",
                "page_content": content,
                "hierarchy": hierarchy,
                "page": i + 1,
                "file_name": file_name,
                "page_image_base64": page_image_base64,
            }
            # Tạo document với từng chunk đã chia
            docs.append(Document(page_content=content.lower(), metadata=metadata))
            doc_ids.append(_id)

    except Exception as e:
        print("Error node_structured_v1 _type 2: ", e)

    return docs, doc_ids


def split_content_by_approx_words(html_content: str, target_words: int = constant.NODE_CHUNK_SIZE_TYPE_1) -> List[str]:
    """
    Hàm chia nội dung HTML. Nếu có bảng, chia theo từng hàng (row).
    Nếu không có bảng, chia văn bản thành các đoạn khoảng target_words từ.
    """
    # Nếu nội dung HTML trống thì trả về danh sách rỗng
    if not html_content.strip():
        return []

    # Phân tích cú pháp HTML bằng BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    chunks = []  # Danh sách chứa các đoạn đã chia
    current_chunk = []  # Tạm giữ nội dung của từng đoạn
    word_count = 0  # Đếm số từ trong chunk

    # Tìm tất cả các hàng <tr> trong bảng nếu có
    rows = soup.find_all('tr')

    if rows:
        # Nếu có bảng, duyệt qua từng hàng <tr> và xử lý như trong bảng
        for row in rows:
            # Lấy nội dung của các ô <td> và nối lại thành một chuỗi
            row_content = " ".join(
                [cell.get_text(strip=True) for cell in row.find_all('td')]
            ).strip()

            # Thêm từng hàng (row) vào chunks
            if row_content:
                chunks.append(row_content)

    else:
        # Nếu không có bảng, xử lý toàn bộ nội dung HTML thành văn bản thuần túy
        text_content = soup.get_text(separator=' ', strip=True)
        words = text_content.split()  # Tách thành danh sách từ

        for word in words:
            # Thêm từng từ vào chunk cho đến khi đạt target_words
            current_chunk.append(word)
            word_count += 1

            if word_count >= target_words:
                # Khi đủ số từ, đóng chunk và tạo chunk mới
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []
                word_count = 0

    # Thêm phần còn lại nếu còn nội dung chưa được thêm vào chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


def node_structured_excel(data, file_name):
    doc_contents = []
    doc_ids = []

    nodes = []

    # Xử lý và hiển thị từng phần thông tin
    for item in data:
        sheet_name = item
        title = data[item]['title']
        datas = data[item]['datas']

        # doc_contents = _clean_data.validate_and_fix_braces(doc_contents)
        parent_hierarchy = file_name + " -> " + title + " -> " + sheet_name

        # Tạo metadata cho node
        metadata = {
            "doc_id": clean.convert_string_to_id(str(sheet_name)+"-"+str(file_name)),
            "summary": "",
            "page_content": datas,
            "hierarchy": parent_hierarchy,
            "page": 1,
            "file_name": file_name,
            "sheet_name": sheet_name,
            "title": title,
            "page_image_base64": ""
        }

        # Thêm node vào danh sách các node
        nodes.append({
            "page_content": parent_hierarchy.lower(),
            "metadata": metadata
        })

    for node in nodes:
        doc_contents.append(Document(page_content=node["page_content"], metadata=node["metadata"]))
        doc_ids.append(node["metadata"]["doc_id"])

    return doc_contents, doc_ids


def node_structured_text(
        text_elements,
        file_name,
        file_type="txt"
) -> tuple[list[Document], list[str]]:
    """
    Generic function for structured text processing
    Supports: txt, csv, html, md, json
    """
    docs = []
    doc_ids = []

    try:
        if not text_elements:
            return docs, doc_ids

        # Xử lý từng element/chunk text
        for i, element in enumerate(text_elements):
            if not element or not element.strip():
                continue

            # Tạo hierarchy dựa trên loại file
            if file_type == "csv":
                hierarchy = f"{file_name} -> Row {i + 1}"
            elif file_type in ["md", "markdown"]:
                hierarchy = f"{file_name} -> Section {i + 1}"
            elif file_type == "json":
                hierarchy = f"{file_name} -> Data {i + 1}"
            elif file_type in ["html", "htm"]:
                hierarchy = f"{file_name} -> Content {i + 1}"
            else:  # txt and others
                hierarchy = f"{file_name} -> Paragraph {i + 1}"

            # Clean content
            clean_content = element.strip()
            
            # Chia content thành chunks nếu quá dài
            content_chunks = split_content_by_approx_words(clean_content, constant.NODE_CHUNK_SIZE_TYPE_1)
            
            # Nếu không có chunks (content rỗng), tạo một chunk trống
            if not content_chunks:
                content_chunks = [clean_content]

            # Tạo documents cho từng chunk
            for chunk_idx, chunk in enumerate(content_chunks):
                if not chunk.strip():
                    continue
                    
                _id = str(uuid.uuid4())
                metadata = {
                    "doc_id": _id,
                    "summary": "",
                    "page_content": clean_content,
                    "hierarchy": hierarchy,
                    "page": i + 1,
                    "file_name": file_name,
                    "file_type": file_type,
                    "chunk_index": chunk_idx,
                    "page_image_base64": "",  # Text files don't have images
                }
                
                # Tạo document với chunk đã chia
                docs.append(Document(page_content=chunk.lower(), metadata=metadata))
                doc_ids.append(_id)

            # Tạo document chính cho toàn bộ element (như các function khác)
            _id = str(uuid.uuid4())
            metadata = {
                "doc_id": _id,
                "summary": "",
                "page_content": clean_content,
                "hierarchy": hierarchy,
                "page": i + 1,
                "file_name": file_name,
                "file_type": file_type,
                "chunk_index": -1,  # -1 indicates main document
                "page_image_base64": "",
            }
            
            docs.append(Document(page_content=clean_content.lower(), metadata=metadata))
            doc_ids.append(_id)

    except Exception as e:
        print(f"Error in node_structured_text: {e}")

    return docs, doc_ids


def node_structured_csv(
        csv_elements,
        file_name
) -> tuple[list[Document], list[str]]:
    """Specialized function for CSV files"""
    return node_structured_text(csv_elements, file_name, "csv")


def node_structured_html(
        html_elements,
        file_name
) -> tuple[list[Document], list[str]]:
    """Specialized function for HTML files"""
    return node_structured_text(html_elements, file_name, "html")


def node_structured_markdown(
        md_elements,
        file_name
) -> tuple[list[Document], list[str]]:
    """Specialized function for Markdown files"""
    return node_structured_text(md_elements, file_name, "md")


def node_structured_json(
        json_elements,
        file_name
) -> tuple[list[Document], list[str]]:
    """Specialized function for JSON files"""
    return node_structured_text(json_elements, file_name, "json")


def node_structured_products_text(
        product_elements: list[str],
        file_name: str
) -> tuple[list[Document], list[str]]:
    """Structured processing for product TXT: one Document per product block."""
    docs: list[Document] = []
    doc_ids: list[str] = []

    try:
        if not product_elements:
            return docs, doc_ids

        for i, block in enumerate(product_elements):
            if not block or not block.strip():
                continue

            lines = block.splitlines()
            first_line = lines[0].strip() if lines else ""

            m = re.match(r"^(\d+)\.\s+(.*)$", first_line)
            product_index = m.group(1) if m else str(i + 1)
            product_title = m.group(2).strip() if m else first_line

            desc_idx = next(
                (idx for idx, ln in enumerate(lines) if "mô tả sản phẩm" in ln.lower()),
                -1
            )
            description = ""
            if desc_idx >= 0:
                description = " ".join(s.strip() for s in lines[desc_idx + 1:]).strip()
            else:
                description = " ".join(s.strip() for s in lines[1:]).strip()

            content = f"{product_title}\n{description}".strip()
            hierarchy = f"{file_name} -> {product_index}. {product_title}"

            _id = str(uuid.uuid4())
            metadata = {
                "doc_id": _id,
                "summary": "",
                "page_content": content,
                "hierarchy": hierarchy,
                "page": int(product_index) if product_index.isdigit() else i + 1,
                "file_name": file_name,
                "file_type": "products_txt",
                "chunk_index": 0,
                "page_image_base64": "",
                "product_title": product_title,
                "product_index": product_index,
            }

            docs.append(Document(page_content=content.lower(), metadata=metadata))
            doc_ids.append(_id)

    except Exception as e:
        print(f"Error in node_structured_products_text: {e}")

    return docs, doc_ids



def node_structured_llm_pdf(
        text_elements,
        file_title="",
        file_name="",
        main_content="",
        document_link=""
) -> tuple[list[Document], list[str]]:
    docs = []
    doc_ids = []

    try:
        if not text_elements:
            return docs, doc_ids

        # Xử lý từng element/chunk text
        hierarchy = f"{file_title} -> {file_name} -> {main_content}"

        # Chia content thành chunks nếu quá dài
        content_chunks = split_content_by_approx_words(text_elements, constant.NODE_CHUNK_SIZE_TYPE_1)
        
        # Nếu không có chunks (content rỗng), tạo một chunk trống
        if not content_chunks:
            content_chunks = [text_elements]

        # Tạo documents cho từng chunk
        for chunk_idx, chunk in enumerate(content_chunks):
            if not chunk.strip():
                continue
                
            _id = str(uuid.uuid4())
            metadata = {
                "doc_id": _id,
                "summary": "",
                "page_content": text_elements,
                "hierarchy": hierarchy,
                "file_title": file_title,
                "file_name": file_name,
                "main_content": main_content,
                "chunk_index": chunk_idx,
                "page_image_base64": "", 
                "document_link": document_link
            }
            
            # Tạo document với chunk đã chia
            docs.append(Document(page_content=chunk.lower(), metadata=metadata))
            doc_ids.append(_id)

        # Tạo document chính cho toàn bộ element (như các function khác)
        _id = str(uuid.uuid4())
        metadata = {
            "doc_id": _id,
            "summary": "",
            "page_content": text_elements,
            "hierarchy": hierarchy,
            "file_title": file_title,
            "file_name": file_name,
            "main_content": main_content,
            "chunk_index": -1,  
            "page_image_base64": "",
            "document_link": document_link
        }
        
        docs.append(Document(page_content=hierarchy.lower(), metadata=metadata))
        doc_ids.append(_id)

    except Exception as e:
        print(f"Error in node_structured_text: {e}")

    return docs, doc_ids