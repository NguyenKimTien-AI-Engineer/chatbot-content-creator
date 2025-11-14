from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import asyncio
import re
import aiofiles
from pathlib import Path
from typing import Union, Optional, List, Dict, Any, Tuple

from langchain_core.documents import Document

from configs import constant
from controllers.modules import upload_files
from controllers.databases.vector.qdrant import collections, qdrant
from controllers.documents.pdf import process_pdf
from controllers.documents.docx import process_docx
from controllers.documents.xlsx import process_xlsx
from controllers.documents.txt import process_txt
from controllers.documents.csv import process_csv
from controllers.documents.html import process_html
from controllers.documents.md import process_md
from controllers.documents.json import process_json
from controllers.modules import node_structured

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


# ===================================================================================
# BUILD DOCS LIKE TEST APPEND PIPELINE
async def build_docs_for_file(
    file_path: str,
    user_id: str,
    language: str = "vie+eng",
) -> Tuple[List[Document], List[str], str]:
    path = Path(file_path)
    file_name = path.name
    ext = path.suffix.lower().lstrip(".")
    folder_path = f"{constant.DATA_USER}/{user_id}"

    if ext == "pdf":
        raw_elements, images = await asyncio.to_thread(
            process_pdf.process_pdf, folder_path, str(path), language
        )
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_pdf, raw_elements, images, file_name
        )
    elif ext in {"doc", "docx"}:
        raw_elements, images = await asyncio.to_thread(process_docx.process_docx, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_docx, raw_elements, images, file_name
        )
    elif ext == "xlsx":
        all_data = await asyncio.to_thread(process_xlsx.process_xlsx, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_excel, all_data, file_name
        )
    elif ext == "txt":
        products, _ = await asyncio.to_thread(process_txt.process_products_txt, str(path))
        if products:
            docs, ids = await asyncio.to_thread(
                node_structured.node_structured_products_text, products, file_name
            )
        else:
            raw_elements, _ = await asyncio.to_thread(process_txt.process_txt, str(path))
            docs, ids = await asyncio.to_thread(
                node_structured.node_structured_text, raw_elements, file_name, "txt"
            )
    elif ext == "csv":
        raw_elements, _ = await asyncio.to_thread(process_csv.process_csv, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_csv, raw_elements, file_name
        )
    elif ext in {"html", "htm"}:
        raw_elements, _ = await asyncio.to_thread(process_html.process_html, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_html, raw_elements, file_name
        )
    elif ext in {"md", "markdown"}:
        raw_elements, _ = await asyncio.to_thread(process_md.process_md, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_markdown, raw_elements, file_name
        )
    elif ext == "json":
        raw_elements, _ = await asyncio.to_thread(process_json.process_json, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_json, raw_elements, file_name
        )
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

    return docs, ids, file_name


# ===================================================================================
# NEW: UPLOAD AND APPEND TO A SPECIFIC COLLECTION (DEFAULT FROM CLIENT)
@router.post("/v1/upload-to-collection")
@router.post("/v1/upload-to-collection/")
async def upload_to_collection_endpoint(
    user_id: Optional[str] = Form("default"),
    collection_name: Optional[str] = Form(""),
    file: Optional[Union[UploadFile, str]] = File(None),
    language: Optional[str] = Form("vie+eng"),
    note: Optional[str] = Form(""),
):
    file_path = ""

    try:
        base_path = constant.DATA + "/" + constant.CHATBOT_NAME
        contents = await file.read()
        await file.seek(0)
        user_dir = Path(base_path) / (user_id or "default")
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / file.filename

        chunk_size = 1024 * 1024
        async with aiofiles.open(file_path, "wb") as f:
            for i in range(0, len(contents), chunk_size):
                await f.write(contents[i: i + chunk_size])
                await asyncio.sleep(0.01)

        docs, ids, file_name = await build_docs_for_file(str(file_path), user_id or "default", language)
        if not docs:
            content = {"status": 400, "message": "Invalid File."}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

        target_collection = (collection_name or "").strip()
        if not target_collection:
            content = {"status": 400, "message": "Missing collection_name."}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

        info = {"collection_name": target_collection, "file_name": file_name, "note": note}
        data_user = await asyncio.to_thread(collections.save_qdrant_collection_user, user_id or "default", info)
        await asyncio.to_thread(collections.save_qdrant_collection_all, info)
        await asyncio.to_thread(qdrant.save_vector_db_as_ids, docs, target_collection, ids)

        content = {
            "status": 200,
            "data": data_user,
            "message": "File appended to collection successfully.",
        }
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        print("Error upload_to_collection: ", e)
        content = {"status": 400, "message": "Error upload_to_collection: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)

    finally:
        try:
            if file_path:
                remove_file(Path(file_path))
        except Exception:
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
