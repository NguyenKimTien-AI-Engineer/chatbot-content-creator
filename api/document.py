from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import asyncio
import re
import aiofiles
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

from configs import constant
from controllers.modules import upload_files
from controllers.databases.vector.qdrant import collections

router = APIRouter()


# --- Models cho request body ---
class CollectionInfo(BaseModel):
    collection_name: str
    file_name: str
    note: str


class SaveUserCollectionRequest(BaseModel):
    user_id: Union[str, int]
    info: Union[CollectionInfo, List[CollectionInfo]]


class SaveAllCollectionsRequest(BaseModel):
    info: Union[CollectionInfo, List[CollectionInfo]]


# ===================================================================================
# UPLOAD FILES
@router.post("/v1/upload-files")
@router.post("/v1/upload-files/")
async def upload_files_endpoint(
        user_id: Optional[str] = Form(""),
        file: Optional[Union[UploadFile, str]] = File(None),
        url: Optional[str] = Form(""),
        language: Optional[str] = Form("vie+eng"),
        note: Optional[str] = Form(""),
):
    file_path = ""

    try:
        path = constant.DATA + "/" + constant.CHATBOT_NAME

        # Lấy tên file
        if url:
            name, extension = upload_files.get_file_name_and_extension(url)
            new_file_name = f"{name}.{extension}"  # Tên file từ URL
        else:
            new_file_name = file.filename  # Tên file từ upload

        # Kiểm tra trùng lặp File
        duplicate, file_content = upload_files.check_all_data_upload(user_id, new_file_name)
        if duplicate:
            content = {
                "status": 200,
                "data": file_content,
                "message": "The file already exists in the system and has been automatically copied to this user ID.",
            }
            return JSONResponse(content=jsonable_encoder(content), status_code=200)

        # Xử lý file tải về hoặc upload
        if url:
            path = path + "/" + new_file_name
            file_path = Path(path)
            await upload_files.download_file_from_url(url, file_path)
        else:
            contents = await file.read()

            await file.seek(0)
            user_dir = Path(path) / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            file_path = user_dir / file.filename

            # Save the uploaded file to disk in chunks
            chunk_size = 1024 * 1024  # 1MB
            async with aiofiles.open(file_path, "wb") as f:
                for i in range(0, len(contents), chunk_size):
                    await f.write(contents[i: i + chunk_size])
                    await asyncio.sleep(0.01)  # Thêm thời gian nghỉ nhỏ

        # Process the uploaded file
        loop = asyncio.get_event_loop()
        answer, data_ = await loop.run_in_executor(
            None,
            upload_files.save_vector_db,
            user_id,
            str(file_path),
            note,
            language,
        )

        if answer:
            content = {
                "status": 200,
                "data": data_,
                "message": "File uploaded and processed successfully.",
            }
            return JSONResponse(content=jsonable_encoder(content), status_code=200)
        else:
            content = {"status": 400, "message": "Invalid File."}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

    except Exception as e:
        print("Error uploading files: ", e)
        content = {"status": 400, "message": "Error uploading files: " + str(e)}

        return JSONResponse(content=jsonable_encoder(content), status_code=400)

    finally:
        if not url:
            try:
                remove_file(file_path)
            except Exception as e:
                pass


def remove_file(file_path_rm):
    try:
        if file_path_rm.exists():
            file_path_rm.unlink()
            print("File removed successfully.")
    except PermissionError as e:
        print("File remove error: ", e)
        pass


# --- Endpoint lưu collection cho 1 user ---
@router.post("/v1/qdrant/collections/user")
@router.post("/v1/qdrant/collections/user/")
async def save_user_collections_endpoint(request: SaveUserCollectionRequest):
    try:
        # chuyển Pydantic model về dict
        infos = request.info
        # nếu chỉ 1 object, convert thành list
        if isinstance(infos, CollectionInfo):
            infos = [infos.dict()]
        else:
            infos = [item.dict() for item in infos]
        result = collections.save_qdrant_collection_user(re.sub(r"\s+", "", request.user_id), infos)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": 200,
                "message": "Lưu thành công",
                "data": result
            })
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({
                "status": 400,
                "message": f"Lỗi khi lưu collections cho user: {e}"
            })
        )


# --- Endpoint lấy tất cả collections của 1 user ---
@router.get("/v1/qdrant/collections/user/{user_id}")
@router.get("/v1/qdrant/collections/user/{user_id}/")
async def read_user_collections_endpoint(user_id: str):
    try:
        result = collections.get_qdrant_collections_user(user_id)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": 200,
                "message": "Lấy dữ liệu thành công",
                "data": result
            })
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({
                "status": 400,
                "message": f"Lỗi khi đọc collections của user: {e}"
            })
        )


# --- Endpoint lưu collection chung (all) ---
@router.post("/v1/qdrant/collections/all")
@router.post("/v1/qdrant/collections/all/")
async def save_all_collections_endpoint(request: SaveAllCollectionsRequest):
    try:
        infos = request.info
        if isinstance(infos, CollectionInfo):
            infos = [infos.dict()]
        else:
            infos = [item.dict() for item in infos]
        result = collections.save_qdrant_collection_all(infos)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": 200,
                "message": "Lưu all collections thành công",
                "data": result
            })
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({
                "status": 400,
                "message": f"Lỗi khi lưu all collections: {e}"
            })
        )


# --- Endpoint lấy tất cả collections chung ---
@router.get("/v1/qdrant/collections/all")
@router.get("/v1/qdrant/collections/all/")
async def read_all_collections_endpoint():
    try:
        result = collections.get_qdrant_collections_all()
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": 200,
                "message": "Lấy all collections thành công",
                "data": result
            })
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({
                "status": 400,
                "message": f"Lỗi khi đọc all collections: {e}"
            })
        )
