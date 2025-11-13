import boto3
import os
import json
import uuid
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from urllib.parse import urlparse, unquote
from pathlib import Path

from configs import constant

from controllers.documents.pdf import process_pdf
from controllers.documents.docx import process_docx
from controllers.documents.xlsx import process_xlsx
from controllers.documents.txt import process_txt
from controllers.documents.csv import process_csv
from controllers.documents.html import process_html
from controllers.documents.md import process_md
from controllers.documents.json import process_json
from controllers.databases.vector.qdrant import collections as qdrant_collections, qdrant
from controllers.modules import node_structured


def save_vector_db(user_id, file_path, note, language="vie+eng"):
    try:
        file_extension = file_path.split(".")[-1].lower()
        folder_path = f"{constant.DATA_USER}/{user_id}"
        file_name = file_path.split("\\")[-1]
        file_name = file_name.split("/")[-1]

        # Ham xu ly file pdf
        if file_extension == "pdf":
            raw_elements, page_image_base64_list = process_pdf.process_pdf(
                folder_path, file_path, language
            )

            docs_text, doc_ids = node_structured.node_structured_pdf(
                raw_elements, page_image_base64_list, file_name
            )

        elif file_extension == "doc" or file_extension == "docx":
            raw_elements, page_image_base64_list = process_docx.process_docx(file_path)

            docs_text, doc_ids = node_structured.node_structured_docx(
                raw_elements, page_image_base64_list, file_name
            )

        elif file_extension == "xlsx":
            all_data = process_xlsx.process_xlsx(file_path)

            docs_text, doc_ids = node_structured.node_structured_excel(all_data, file_name)

        elif file_extension == "txt":
            raw_elements, _ = process_txt.process_txt(file_path)
            docs_text, doc_ids = node_structured.node_structured_text(raw_elements, file_name, "txt")

        elif file_extension == "csv":
            raw_elements, _ = process_csv.process_csv(file_path)
            docs_text, doc_ids = node_structured.node_structured_csv(raw_elements, file_name)

        elif file_extension in ["html", "htm"]:
            raw_elements, _ = process_html.process_html(file_path)
            docs_text, doc_ids = node_structured.node_structured_html(raw_elements, file_name)

        elif file_extension in ["md", "markdown"]:
            raw_elements, _ = process_md.process_md(file_path)
            docs_text, doc_ids = node_structured.node_structured_markdown(raw_elements, file_name)

        elif file_extension == "json":
            raw_elements, _ = process_json.process_json(file_path)
            docs_text, doc_ids = node_structured.node_structured_json(raw_elements, file_name)

        else:
            raise ValueError(f"Unsupported file type: .{file_extension}")

        if docs_text:
            collection_name = f"{constant.CHATBOT_NAME}_{user_id}_{uuid.uuid4()}"
            print(f"Collection name: {collection_name}")

            info = {"collection_name": collection_name, "file_name": file_name, "note": note}
            data_ = qdrant_collections.save_qdrant_collection_user(user_id, info)

            qdrant_collections.save_qdrant_collection_all(info)

            qdrant.save_vector_db_as_ids(docs_text, collection_name, doc_ids)

            return True, data_

        else:
            return False, None

    except ValueError as ve:
        print(f"ValueError in save_vector_db: {ve}")
        return False, None


def check_all_data_upload(user_id, new_file_name):
    duplicate = False
    file_content = []

    try:
        if os.path.exists(constant.ALL_DATA_UPLOAD):
            with open(constant.ALL_DATA_UPLOAD, "r", encoding="utf-8") as list_file:
                collections = json.load(list_file)

                # Kiểm tra từng entry trong list
                for entry in collections:
                    if entry.get("file_name") == new_file_name:
                        collection_name = entry.get("collection_name")
                        file_name = entry.get("file_name")
                        note = entry.get("note")

                        info = {"collection_name": collection_name, "file_name": file_name, "note": note}

                        duplicate = True
                        file_content = qdrant_collections.save_qdrant_collection_user(user_id, info)

        return duplicate, file_content
    except Exception as e:
        print(f"Error in check_all_data_upload: {e}")
        return False, None

# S3
def parse_s3_url(s3_url):
    try:
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc.split('.')[0]  # Tên bucket là phần đầu tiên của netloc
        file_key = unquote(parsed_url.path.lstrip('/'))  # Loại bỏ dấu '/' ở đầu và giải mã URL
        return bucket_name, file_key
    except Exception as e:
        print(f"⛔ Lỗi khi phân giải URL: {e}")
        return None, None


# Kiểm tra file tồn tại
def check_file_exists(bucket_name, file_key, aws_access_key_id, aws_secret_access_key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        print("✅ File tồn tại.")
        return True
    except Exception as e:
        print(f"⛔ File không tồn tại hoặc không có quyền: {e}")
        return False


# Hàm tải file từ S3
def download_pdf_from_s3(bucket_name, file_key, download_path, aws_access_key_id, aws_secret_access_key):
    try:
        # Tạo thư mục nếu chưa tồn tại
        directory = os.path.dirname(download_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Thư mục đã được tạo: {directory}")

        # Tải file từ S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        s3_client.download_file(bucket_name, file_key, download_path)
        print(f"🎉 File đã được tải về: {download_path}")

    except NoCredentialsError:
        print("⛔ Lỗi: Không tìm thấy thông tin xác thực AWS.")
    except PartialCredentialsError:
        print("⛔ Lỗi: Thông tin xác thực AWS không đầy đủ.")
    except FileNotFoundError as e:
        print(f"⛔ Lỗi: File không tồn tại hoặc không thể truy cập: {e}")
        # Tạo file trống nếu cần thiết
        with open(download_path, 'w') as file:
            file.write("")  # File trống
        print(f"✅ File trống đã được tạo tại: {download_path}")
    except Exception as e:
        print(f"⛔ Lỗi khác: {e}")


async def download_file_from_url(url: str, save_path: Path):
    # Phân giải URL
    bucket_name, file_key = parse_s3_url(url)

    # Kiểm tra và tải file
    if bucket_name and file_key:
        if check_file_exists(bucket_name, file_key, constant.AWS_ACCESS_KEY_ID, constant.AWS_SECRET_ACCESS_KEY):
            download_pdf_from_s3(bucket_name, file_key, save_path, constant.AWS_ACCESS_KEY_ID, constant.AWS_SECRET_ACCESS_KEY)
        else:
            print("⛔ Không thể tải file.")
    else:
        print("⛔ URL không hợp lệ.")


def get_file_name_and_extension(url: str):
    """Lấy tên file và phần mở rộng từ URL."""
    # Phân tích URL
    parsed_url = urlparse(url)
    # Lấy đường dẫn cuối cùng sau dấu /
    file_name = parsed_url.path.split("/")[-1]
    # Tách tên file và phần mở rộng
    name, extension = file_name.rsplit(".", 1) if "." in file_name else (file_name, None)

    return name, extension

