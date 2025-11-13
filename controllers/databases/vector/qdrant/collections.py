import os
import json

from configs import constant


def save_qdrant_collection_user(user_id, info):
    try:
        # info format: info = {"collection_name": collection_name, "file_name": file_name, "note": note}

        json_file_path = (
            constant.DATA_USER
            + "/"
            + constant.CHATBOT_NAME
            + "/"
            + str(user_id)
            + "/"
            + "qdrant_collections.json"
        )

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        # Đọc dữ liệu hiện có từ file JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []

        # Chuyển `info` thành list nếu nó là dictionary
        if isinstance(info, dict):
            info = [info]

        # Tạo set chứa các mục đã tồn tại để kiểm tra trùng lặp
        existing_items = {json.dumps(item, sort_keys=True) for item in data}

        # Chỉ thêm các mục mới vào `data`
        new_items = [item for item in info if json.dumps(item, sort_keys=True) not in existing_items]
        data.extend(new_items)  # Thêm các mục mới vào `data`

        # Ghi lại dữ liệu vào file JSON
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return data
    except Exception as e:
        print(f"Error save_qdrant_collection_user: {e}")
        return None


def save_qdrant_collection_all(info):
    try:
        # info format: info = {"collection_name": collection_name, "file_name": file_name, "note": note}

        json_file_path = constant.ALL_DATA_UPLOAD

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        # Đọc dữ liệu hiện có từ file JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []

        # Chuyển `info` thành list nếu nó là dictionary
        if isinstance(info, dict):
            info = [info]

        # Tạo set chứa các mục đã tồn tại để kiểm tra trùng lặp
        existing_items = {json.dumps(item, sort_keys=True) for item in data}

        # Chỉ thêm các mục mới vào `data`
        new_items = [item for item in info if json.dumps(item, sort_keys=True) not in existing_items]
        data.extend(new_items)  # Thêm các mục mới vào `data`

        # Ghi lại dữ liệu vào file JSON
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return data
    except Exception as e:
        print(f"Error save_qdrant_collection_user: {e}")
        return None


def get_qdrant_collections_user(user_id):
    """
    Đọc và trả về danh sách collections của user từ file qdrant_collections.json.
    Nếu file không tồn tại sẽ trả về [].
    """
    try:
        json_file_path = os.path.join(
            constant.DATA_USER,
            constant.CHATBOT_NAME,
            str(user_id),
            "qdrant_collections.json"
        )
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        # File chưa có → chưa có collection nào
        return []
    except Exception as e:
        print(f"Error get_qdrant_collections_user: {e}")
        return None


def get_qdrant_collections_all():
    """
    Đọc và trả về danh sách tất cả collections từ file ALL_DATA_UPLOAD.
    Nếu file không tồn tại sẽ trả về [].
    """
    try:
        json_file_path = constant.ALL_DATA_UPLOAD
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        # File chưa có → chưa có collection nào
        return []
    except Exception as e:
        print(f"Error get_qdrant_collections_all: {e}")
        return None

