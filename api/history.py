"""
History API router cho Agent Content Generator.

Cung cấp CRUD operations cho history management với MongoDB.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends, status, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from collections import defaultdict
import time
import uuid

from controllers.databases.nosql.mongodb import get_mongodb_manager, MongoDBManager

router = APIRouter()

active_ws_connections: Dict[str, List[WebSocket]] = defaultdict(list)

async def broadcast_session_update(user_id: str, payload: Dict[str, Any]) -> None:
    conns = active_ws_connections.get(user_id, [])
    if not conns:
        return
    data = {"type": "session_update", **payload}
    living: List[WebSocket] = []
    for ws in conns:
        try:
            await ws.send_json(data)
            living.append(ws)
        except Exception:
            try:
                await ws.close()
            except Exception:
                pass
    active_ws_connections[user_id] = living

# Rate limiting storage - in production, use Redis or similar
rate_limit_storage: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # Maximum requests per window
RATE_LIMIT_WINDOW = 60  # Time window in seconds


def check_rate_limit(user_id: str) -> bool:
    """
    Kiểm tra rate limit cho user.
    
    Args:
        user_id: ID của user
        
    Returns:
        bool: True nếu trong giới hạn, False nếu vượt quá
    """
    current_time = time.time()
    
    # Get requests for this user
    user_requests = rate_limit_storage[user_id]
    
    # Remove requests outside the time window
    user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < RATE_LIMIT_WINDOW]
    
    # Check if limit exceeded
    if len(user_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    user_requests.append(current_time)
    return True


def convert_references_to_schema(references: Optional[List]) -> Optional[List[Dict[str, str]]]:
    """
    Chuyển đổi references sang schema chuẩn với đầy đủ thông tin.
    
    Args:
        references: Danh sách references (có thể là schema cũ hoặc mới)
        
    Returns:
        List[Dict]: Danh sách references theo schema chuẩn
    """
    if not references:
        return None
    
    converted_references = []
    
    for ref in references:
        if isinstance(ref, dict):
            # Nếu đã là schema mới với đầy đủ trường
            if all(key in ref for key in ['doc_id', 'title', 'source', 'excerpt']):
                converted_references.append(ref)
            # Nếu là schema cũ (chỉ có title và content)
            elif 'title' in ref and 'content' in ref:
                converted_references.append({
                    "doc_id": str(uuid.uuid4()),  # Tạo ID mới
                    "title": ref['title'],
                    "source": ref.get('source', 'unknown'),  # Mặc định nếu không có
                    "excerpt": ref['content']
                })
            # Nếu chỉ có title
            elif 'title' in ref:
                converted_references.append({
                    "doc_id": str(uuid.uuid4()),
                    "title": ref['title'],
                    "source": ref.get('source', 'unknown'),
                    "excerpt": ref.get('content', ref.get('excerpt', ''))
                })
            else:
                # Nếu không có cấu trúc rõ ràng, tạo từ dict
                converted_references.append({
                    "doc_id": str(uuid.uuid4()),
                    "title": ref.get('title', 'Tài liệu tham khảo'),
                    "source": ref.get('source', 'unknown'),
                    "excerpt": ref.get('content', ref.get('excerpt', str(ref)))
                })
        else:
            # Nếu không phải dict, chuyển đổi sang string
            converted_references.append({
                "doc_id": str(uuid.uuid4()),
                "title": "Tài liệu tham khảo",
                "source": "unknown",
                "excerpt": str(ref)
            })
    
    return converted_references if converted_references else None


def get_rate_limit_info(user_id: str) -> Dict[str, any]:
    """
    Get rate limit information for user.
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict: Thông tin rate limit
    """
    current_time = time.time()
    user_requests = rate_limit_storage[user_id]
    
    # Remove old requests
    user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < RATE_LIMIT_WINDOW]
    
    return {
        "limit": RATE_LIMIT_REQUESTS,
        "window": RATE_LIMIT_WINDOW,
        "current": len(user_requests),
        "remaining": max(0, RATE_LIMIT_REQUESTS - len(user_requests))
    }


class ReferenceItem(BaseModel):
    doc_id: str = Field(...)
    title: str = Field(...)
    source: str = Field(...)
    excerpt: str = Field(...)


class HistoryCreateRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    session_id: Optional[str] = Field(default="", max_length=100)
    query: str = Field(..., min_length=1, max_length=5000)
    answer: str = Field(..., min_length=1, max_length=10000)
    feedback: Optional[str] = Field(default="", max_length=1000)
    feedback_status: Optional[str] = Field(default="", max_length=50)
    reference: Optional[List[Any]] = Field(default=None)
    chart: Optional[dict] = Field(default=None)
    image_url: Optional[str] = Field(default=None)


class HistoryItemResponse(BaseModel):
    """Response model cho history item"""
    history_id: str
    user_id: str
    session_id: str
    query: str
    answer: str
    feedback: Optional[str] = ""
    feedback_status: Optional[str] = ""
    reference: Optional[List] = None
    chart: Optional[dict] = None
    image_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None


class HistoryListResponse(BaseModel):
    """Response model cho danh sách history"""
    success: bool = True
    message: str = "Thành công"
    data: List[HistoryItemResponse]
    total: int
    page: int = 1
    limit: int = 20


class HistoryCreateResponse(BaseModel):
    """Response model cho tạo history mới"""
    success: bool = True
    message: str = "Lưu lịch sử thành công"
    data: dict


class HistoryDeleteResponse(BaseModel):
    """Response model cho xóa history"""
    success: bool = True
    message: str = "Xóa lịch sử thành công"


class ErrorResponse(BaseModel):
    """Response model cho lỗi"""
    success: bool = False
    message: str
    error: Optional[str] = None


def get_current_user_id(request: Request) -> str:
    """
    Lấy user ID từ request (từ token hoặc session).
    Implement token-based authentication với Bearer token và rate limiting.
    """
    # Lấy Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu Authorization header"
        )
    
    # Validate Bearer token format
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header phải có format 'Bearer <token>'"
        )
    
    # Extract token
    token = auth_header.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không được để trống"
        )
    
    # Validate token format (simple validation - in production, use JWT or similar)
    # For now, we'll use the token as user_id if it meets basic requirements
    if len(token) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token quá ngắn"
        )
    
    # Check rate limit
    if not check_rate_limit(token):
        rate_info = get_rate_limit_info(token)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {rate_info['limit']} requests per {rate_info['window']} seconds. Remaining: {rate_info['remaining']}"
        )
    
    # In a real implementation, you would:
    # 1. Verify JWT signature
    # 2. Check token expiration
    # 3. Validate against a token blacklist
    # 4. Extract user_id from token claims
    
    # For this implementation, we'll use the token as user_id
    # In production, replace this with proper JWT validation
    return token


@router.post(
    "/v1/history",
    response_model=HistoryCreateResponse,
    summary="Lưu lịch sử chat vào MongoDB",
    description="Lưu một bản ghi lịch sử mới vào database"
)
async def create_history(
    request: HistoryCreateRequest,
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> HistoryCreateResponse:
    """
    Lưu lịch sử chat mới vào MongoDB.
    
    Args:
        request: HistoryCreateRequest với thông tin lịch sử
        db: MongoDB manager instance
        current_user: User ID hiện tại
        
    Returns:
        HistoryCreateResponse: Kết quả lưu lịch sử
    """
    try:
        # Validate user_id matches current user
        if request.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập"
            )
        
        history_id = str(uuid.uuid4())
        session_id = (request.session_id or "").strip() or str(uuid.uuid4())
        
        # Convert references to proper schema
        converted_references = convert_references_to_schema(request.reference)
        
        # Validation: Check if references should exist based on content
        # If the answer mentions documents, sources, or references but no references are provided
        answer_lower = request.answer.lower()
        query_lower = request.query.lower()
        
        # Keywords that suggest references should exist
        ref_keywords = ['tài liệu', 'document', 'source', 'nguồn', 'tham khảo', 'reference', 'theo', 'according']
        has_ref_keywords = any(keyword in answer_lower for keyword in ref_keywords)
        
        # If answer suggests references exist but none are provided, add a warning
        if has_ref_keywords and not converted_references:
            print(f"Cảnh báo: Câu trả lời có vẻ như cần tài liệu tham khảo nhưng không có references nào được cung cấp. User: {request.user_id}, Query: {request.query[:50]}...")
            # Optionally, we could raise an exception or add default references
            # For now, we just log a warning to help with debugging
        
        # Save to MongoDB
        result = await db.save_history(
            user_id=request.user_id,
            history_id=history_id,
            session_id=session_id,
            query=request.query,
            answer=request.answer,
            feedback=request.feedback or "",
            feedback_status=request.feedback_status or "",
            references=converted_references,
            chart=request.chart,
            image_url=request.image_url
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể lưu lịch sử"
            )
        await broadcast_session_update(
            current_user,
            {
                "session_id": session_id,
                "preview": request.query,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        return HistoryCreateResponse(
            message="Lưu lịch sử thành công",
            data={
                "history_id": history_id,
                "inserted_id": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi lưu lịch sử: {str(e)}"
        )


@router.get(
    "/v1/history",
    response_model=HistoryListResponse,
    summary="Lấy danh sách lịch sử",
    description="Lấy danh sách lịch sử của người dùng với các bộ lọc"
)
async def get_history(
    user_id: Optional[str] = Query(None, description="Lọc theo user ID"),
    session_id: Optional[str] = Query(None, description="Lọc theo session ID"),
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng bản ghi mỗi trang"),
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> HistoryListResponse:
    """
    Lấy danh sách lịch sử từ MongoDB.
    
    Args:
        user_id: User ID để lọc (optional)
        session_id: Session ID để lọc (optional)
        page: Số trang
        limit: Số lượng bản ghi mỗi trang
        db: MongoDB manager instance
        current_user: User ID hiện tại
        
    Returns:
        HistoryListResponse: Danh sách lịch sử
    """
    try:
        # Use current_user if user_id not provided
        filter_user_id = user_id or current_user
        
        # Validate access
        if user_id and user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập"
            )
        
        # Get history from MongoDB
        histories = await db.get_user_history(
            user_id=filter_user_id,
            session_id=session_id,
            limit=limit,
            skip=(page - 1) * limit
        )
        
        # Convert to response format
        history_items = []
        for history in histories:
            history_items.append(HistoryItemResponse(
                history_id=history.get("history_id", ""),
                user_id=history.get("user_id", ""),
                session_id=history.get("session_id", ""),
                query=history.get("query", ""),
                answer=history.get("answer", ""),
                feedback=history.get("feedback", ""),
                feedback_status=history.get("feedback_status", ""),
                reference=history.get("reference", []),
                chart=history.get("chart"),
                image_url=history.get("image_url"),
                timestamp=history.get("timestamp"),
                created_at=history.get("created_at")
            ))
        
        # Get total count
        total = len(history_items)  # For now, get actual count would need separate query
        
        return HistoryListResponse(
            message="Lấy danh sách lịch sử thành công",
            data=history_items,
            total=total,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi lấy lịch sử: {str(e)}"
        )


@router.delete(
    "/v1/history/{history_id}",
    response_model=HistoryDeleteResponse,
    summary="Xóa bản ghi lịch sử",
    description="Xóa một bản ghi lịch sử theo ID"
)
async def delete_history(
    history_id: str,
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> HistoryDeleteResponse:
    """
    Xóa lịch sử theo ID.
    
    Args:
        history_id: ID của history cần xóa
        db: MongoDB manager instance
        current_user: User ID hiện tại
        
    Returns:
        HistoryDeleteResponse: Kết quả xóa
    """
    try:
        # First, get the history to verify ownership
        history = await db.get_history_by_id(history_id)
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy lịch sử"
            )
        
        # Verify ownership
        if history.get("user_id") != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xóa lịch sử này"
            )
        
        # Delete from MongoDB
        success = await db.delete_history(history_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể xóa lịch sử"
            )
        
        return HistoryDeleteResponse(
            message="Xóa lịch sử thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi xóa lịch sử: {str(e)}"
        )


@router.get(
    "/v1/history/sessions",
    response_model=dict,
    summary="Lấy danh sách sessions",
    description="Lấy tất cả sessions của người dùng hiện tại"
)
async def get_user_sessions(
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> dict:
    """
    Lấy danh sách sessions của user.
    
    Args:
        db: MongoDB manager instance
        current_user: User ID hiện tại
        
    Returns:
        dict: Danh sách sessions
    """
    try:
        sessions = await db.get_user_sessions(current_user)
        sessions_sorted = sorted(
            sessions,
            key=lambda s: s.get("last_activity") or s.get("updated_at") or s.get("created_at") or "",
            reverse=True,
        )
        total = len(sessions_sorted)
        paged = sessions_sorted[skip: skip + limit]
        enriched = []
        for s in paged:
            try:
                sid = s.get("session_id") or s.get("id") or ""
                latest = await db.get_user_history(
                    user_id=current_user,
                    session_id=sid,
                    limit=1,
                    skip=0,
                )
                if latest:
                    item = latest[0]
                    q = str(item.get("query", ""))
                    head = q.split("\n")[0] if q else ""
                    s["preview"] = head or "New chat"
                else:
                    s["preview"] = "New chat"
            except Exception:
                s["preview"] = "New chat"
            enriched.append(s)
        return {
            "success": True,
            "message": "Lấy danh sách sessions thành công",
            "data": enriched,
            "total": total,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi lấy sessions: {str(e)}"
        )


@router.get(
    "/v1/history/rate-limit",
    response_model=dict,
    summary="Lấy thông tin rate limit",
    description="Lấy thông tin rate limit hiện tại của user"
)
async def get_rate_limit_status(
    current_user: str = Depends(get_current_user_id)
) -> dict:
    """
    Lấy thông tin rate limit của user hiện tại.
    
    Args:
        current_user: User ID hiện tại
        
    Returns:
        dict: Thông tin rate limit
    """
    try:
        rate_info = get_rate_limit_info(current_user)
        
        return {
            "success": True,
            "message": "Lấy thông tin rate limit thành công",
            "data": rate_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi lấy thông tin rate limit: {str(e)}"
        )


@router.get("/v1/history/image/{image_id}")
@router.get("/v1/history/image/{image_id}/")
async def get_history_image(
    image_id: str,
    current_user: str = Depends(get_current_user_id)
):
    """
    Lấy ảnh từ lịch sử chat.
    Chỉ cho phép người dùng sở hữu ảnh mới có thể truy cập.
    """
    try:
        db = await get_mongodb_manager()
        
        # Get image from MongoDB
        image_data = await db.get_image(image_id)
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy ảnh"
            )
        
        # Check if user owns the image
        if image_data.get("user_id") != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập ảnh này"
            )
        
        # Return image with proper content type
        return Response(
            content=image_data["binary_data"],
            media_type=image_data["content_type"],
            headers={
                "Content-Disposition": f"inline; filename=image_{image_id}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi lấy ảnh: {str(e)}"
        )

@router.websocket("/ws/history")
async def ws_history(websocket: WebSocket):
    try:
        token = websocket.query_params.get("token")
        if not token or len(token) < 8:
            await websocket.accept()
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        user_id = token
        active_ws_connections[user_id].append(websocket)
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        try:
            for uid, lst in list(active_ws_connections.items()):
                if websocket in lst:
                    lst.remove(websocket)
                    if not lst:
                        active_ws_connections.pop(uid, None)
                    break
        except Exception:
            pass
@router.delete(
    "/v1/history/sessions/{session_id}",
    response_model=dict,
    summary="Xóa một session",
    description="Xóa session và toàn bộ lịch sử của nó"
)
async def delete_session(
    session_id: str,
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> dict:
    try:
        success = await db.delete_session(current_user, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể xóa session {session_id} cho user {current_user}"
            )
        return {
            "success": True,
            "message": "Xóa session thành công",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi xóa session: {str(e)}"
        )

@router.post(
    "/v1/history/sessions/delete",
    response_model=dict,
    summary="Xóa session (fallback)",
    description="Xóa session và toàn bộ lịch sử của nó bằng POST"
)
async def delete_session_fallback(
    payload: Dict[str, str],
    db: MongoDBManager = Depends(get_mongodb_manager),
    current_user: str = Depends(get_current_user_id)
) -> dict:
    try:
        session_id = payload.get("session_id", "")
        if not session_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thiếu session_id")
        success = await db.delete_session(current_user, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể xóa session {session_id} cho user {current_user} (fallback)"
            )
        return {
            "success": True,
            "message": "Xóa session thành công",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi xóa session: {str(e)}"
        )