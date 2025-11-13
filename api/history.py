from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import asyncio
import os
from typing import Union, List, Dict, Any

from controllers.data import history
from configs import constant

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


