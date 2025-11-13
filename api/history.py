from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import asyncio
import os
from typing import Union, List, Dict, Any, Optional

from controllers.data import history
from configs import constant
from controllers.databases.nosql.mongodb import get_mongodb_manager, MongoDBManager
from datetime import datetime

router = APIRouter()


class History(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""


# Get user history
@router.post("/v1/history")
@router.post("/v1/history/")
async def get_user_history_endpoint(request: History):
    print("| Get User History API")
    try:
        files_path = f"{constant.DATA_HISTORY}/{request.user_id}"
        print(f"Files path: {files_path}")

        user_histories = []

        if os.path.exists(files_path):
            print(f"Files path exists: {files_path}")
            try:
                loop = asyncio.get_event_loop()
                his = await loop.run_in_executor(
                    None, history.get_all_history_user, request.user_id
                )
                user_histories = his
            except Exception as e:
                content = {"status": 400, "message": "fail", "error": str(e)}
                return JSONResponse(content=jsonable_encoder(content), status_code=400)

        if request.history_id:
            print(f"History ID: {request.history_id}")
            print(user_histories)
            try:
                final_user_histories = [item for item in user_histories if any(
                    item.get("history_id") == request.history_id
                )]
            except Exception as e:
                final_user_histories = [
                    entry
                    for sublist in user_histories
                    for entry in sublist
                    if entry.get("history_id") == request.history_id
                ]

        elif request.session_id:
            print(f"Session ID: {request.session_id}")
            his = history.get_history(request.user_id, request.session_id)
            final_user_histories = his
        else:
            print("No session ID or history ID provided.")
            final_user_histories = user_histories

        content = {
            "status": 200,
            "data": final_user_histories,
            "message": "success"
        }
        return JSONResponse(content=jsonable_encoder(content), status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# Update feedback for chat history
class FeedbackUpdate(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    history_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    new_feedback: Union[str, int, List[Any], Dict[str, Any]] = ""
    new_feedback_status: Union[str, int, List[Any], Dict[str, Any]] = ""


@router.post("/v1/update-feedback-history")
@router.post("/v1/update-feedback-history/")
async def update_feedback_endpoint(request: FeedbackUpdate):
    print("| Update Feedback API")
    try:
        try:
            loop = asyncio.get_event_loop()
            user_histories, _data = await loop.run_in_executor(
                None, history.update_feedback, request.user_id, request.history_id, request.new_feedback, request.new_feedback_status, request.session_id
            )
        except Exception as e:
            content = {"status": 400, "message": "Feedback updated fail: " + str(e)}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

        if user_histories:
            content = {
                "status": 200,
                "data": _data,
                "message": "Feedback updated successfully",
            }
            return JSONResponse(content=jsonable_encoder(content), status_code=200)

        else:
            content = {"status": 400, "message": "History not found."}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# Delete chat history
class DeleteHistories(BaseModel):
    user_id: Union[str, int, List[Any], Dict[str, Any]] = ""
    session_id: Union[str, int, List[Any], Dict[str, Any]] = ""


@router.post("/v1/delete-history")
@router.post("/v1/delete-history/")
async def delete_history_endpoint(request: DeleteHistories):
    print("| Delete History API")
    try:
        path_json = f"{constant.DATA_HISTORY}/{request.user_id}/{request.session_id}.json"

        if os.path.exists(path_json):
            try:
                os.remove(path_json)
                content = {"status": 200, "message": "success"}
                return JSONResponse(content=jsonable_encoder(content), status_code=200)
            except Exception as e:
                content = {"status": 500, "message": f"Error deleting files: {str(e)}"}
                return JSONResponse(content=jsonable_encoder(content), status_code=500)
        else:
            content = {"status": 400, "message": "fail"}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)

    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


# =========================
# MongoDB Chat Histories API
# =========================

class MessageItem(BaseModel):
    role: str
    content: Union[str, Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[Any] = None

class SenderInfo(BaseModel):
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    gender: Optional[str] = None
    id: Optional[str] = None
    status: Optional[int] = None
    message: Optional[str] = None


class CreateConversationRequest(BaseModel):
    conversation_id: str
    user_id: Optional[str] = None
    first_message: Optional[MessageItem] = None
    messages: Optional[List[MessageItem]] = None
    updated_at: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    # Extended fields aligned with json_history.json
    history_id: Optional[Union[str, int]] = None
    session_id: Optional[Union[str, int]] = None
    status: Optional[str] = "active"
    query: Optional[Union[str, int]] = None
    answer: Optional[Any] = None
    answer_segments: Optional[List[Dict[str, Any]]] = None
    media: Optional[Dict[str, Any]] = None
    company_id: Optional[str] = None
    customer_id: Optional[str] = None
    sender_info: Optional[SenderInfo] = None
    bot_id: Optional[str] = None
    social_id: Optional[str] = None
    social_page_id: Optional[str] = None
    social_access_link: Optional[str] = None
    created_at: Optional[Any] = None


class AppendMessageRequest(BaseModel):
    conversation_id: str
    message: MessageItem


class GetConversationRequest(BaseModel):
    conversation_id: str


class ListConversationsRequest(BaseModel):
    user_id: str
    page: Optional[int] = 1
    limit: Optional[int] = 20


class DeleteConversationRequest(BaseModel):
    conversation_id: str


@router.post("/v1/histories/create")
@router.post("/v1/histories/create/")
async def histories_create_endpoint(request: CreateConversationRequest, manager: MongoDBManager = Depends(get_mongodb_manager)):
    try:
        # Sanitize user_id and conversation_id to avoid type errors
        user_id = str(request.user_id or "default_user").strip() or "default_user"
        conversation_id = str(request.conversation_id or request.history_id or request.session_id or "").strip()
        if not conversation_id:
            conversation_id = f"conv_{int(datetime.utcnow().timestamp()*1000)}"

        first_message = request.first_message.model_dump() if request.first_message else None
        messages: Optional[List[Dict[str, Any]]] = None
        if request.messages:
            messages = [m.model_dump() for m in request.messages]

        extra_document: Dict[str, Any] = {
            "history_id": request.history_id,
            "session_id": request.session_id,
            "status": request.status,
            "query": request.query,
            "answer": request.answer,
            "answer_segments": request.answer_segments,
            "media": request.media,
            "company_id": request.company_id,
            "customer_id": request.customer_id,
            "sender_info": request.sender_info.model_dump() if request.sender_info else None,
            "bot_id": request.bot_id,
            "social_id": request.social_id,
            "social_page_id": request.social_page_id,
            "social_access_link": request.social_access_link,
            "created_at": request.created_at,
        }

        ok = await manager.create_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            first_message=first_message,
            metadata=request.metadata,
            messages=messages,
            updated_at=request.updated_at,
            extra_document=extra_document,
        )
        if not ok:
            content = {"status": 400, "message": "create_conversation failed"}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)
        content = {"status": 200, "message": "success"}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/histories/append")
@router.post("/v1/histories/append/")
async def histories_append_endpoint(request: AppendMessageRequest, manager: MongoDBManager = Depends(get_mongodb_manager)):
    try:
        ok = await manager.append_message(request.conversation_id, request.message.model_dump())
        if not ok:
            content = {"status": 400, "message": "append_message failed"}
            return JSONResponse(content=jsonable_encoder(content), status_code=400)
        content = {"status": 200, "message": "success"}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/histories/get")
@router.post("/v1/histories/get/")
async def histories_get_endpoint(request: GetConversationRequest, manager: MongoDBManager = Depends(get_mongodb_manager)):
    try:
        doc = await manager.get_conversation(request.conversation_id)
        content = {"status": 200, "message": "success", "data": doc}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/histories/list")
@router.post("/v1/histories/list/")
async def histories_list_endpoint(request: ListConversationsRequest, manager: MongoDBManager = Depends(get_mongodb_manager)):
    try:
        page = max(1, int(request.page or 1))
        limit = max(1, min(100, int(request.limit or 20)))
        skip = (page - 1) * limit
        items = await manager.list_conversations(request.user_id, limit=limit, skip=skip)
        total = await manager.count_conversations_by_user(request.user_id)
        content = {"status": 200, "message": "success", "data": {"items": items, "page": page, "limit": limit, "total": total}}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


@router.post("/v1/histories/delete")
@router.post("/v1/histories/delete/")
async def histories_delete_endpoint(request: DeleteConversationRequest, manager: MongoDBManager = Depends(get_mongodb_manager)):
    try:
        ok = await manager.delete_conversation(request.conversation_id)
        if not ok:
            content = {"status": 404, "message": "conversation not found"}
            return JSONResponse(content=jsonable_encoder(content), status_code=404)
        content = {"status": 200, "message": "success"}
        return JSONResponse(content=jsonable_encoder(content), status_code=200)
    except Exception as e:
        content = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(content), status_code=400)


