# MongoDB History Storage Implementation

## Overview
Đã mở rộng hệ thống lưu trữ lịch sử chat từ JSON files sang MongoDB để cải thiện hiệu suất và khả năng mở rộng.

## Changes Made

### 1. MongoDBManager Class Updates (`controllers/databases/nosql/mongodb.py`)
- **Thêm history collection**: `self.history_collection`
- **Tạo indexes cho history**:
  - `user_id + session_id` cho queries nhanh
  - `history_id` unique index
  - `timestamp` cho sorting
  - `user_id + timestamp` cho user-based queries

### 2. New MongoDB History Functions

#### Save History
```python
async def save_history_mongodb(user_id: str, history_id: str, session_id: str, query: str, 
                              answer: str, feedback: str, feedback_status: str, 
                              references: Any, chart: Any) -> Optional[str]
```

#### Get History
```python
async def get_history_mongodb(user_id: str, session_id: str) -> list
```

#### Get All User History
```python
async def get_all_history_user_mongodb(user_id: str) -> list
```

#### Update Feedback
```python
async def update_feedback_mongodb(user_id: str, history_id: str, new_feedback: str, 
                                 new_feedback_status: str, session_id: str = None) -> tuple[bool, list]
```

#### Get History Context
```python
async def get_history_context_mongodb_v1(user_id: str, query: str, session_id: str, limit: int = 15) -> str
async def get_history_context_v2_mongodb(user_id: str, query: str, session_id: str, limit: int = 5) -> str
```

### 3. MongoDB Collection Structure
```json
{
  "history_id": "uuid-string",
  "user_id": "user-identifier",
  "session_id": "session-identifier", 
  "query": "user query text",
  "answer": "ai response text",
  "feedback": "user feedback",
  "feedback_status": "positive/negative/neutral",
  "reference": ["ref1", "ref2"],
  "chart": null,
  "timestamp": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Usage Examples

### 1. Save Chat History
```python
from controllers.data.history import save_history_mongodb

result = await save_history_mongodb(
    user_id="user123",
    history_id=None,  # Will auto-generate UUID
    session_id="session456", 
    query="How to create content?",
    answer="Here are the steps to create content...",
    feedback="",
    feedback_status="",
    references=["doc1", "doc2"],
    chart=None
)
```

### 2. Retrieve Chat History
```python
from controllers.data.history import get_history_mongodb

history = await get_history_mongodb("user123", "session456")
for entry in history:
    print(f"Query: {entry['query']}")
    print(f"Answer: {entry['answer']}")
```

### 3. Update Feedback
```python
from controllers.data.history import update_feedback_mongodb

success, updated = await update_feedback_mongodb(
    user_id="user123",
    history_id="history-uuid",
    new_feedback="Very helpful!",
    new_feedback_status="positive"
)
```

### 4. Get History Context for AI
```python
from controllers.data.history import get_history_context_mongodb_v1

context = await get_history_context_mongodb_v1(
    user_id="user123",
    query="Tell me more about content creation",
    session_id="session456"
)
```

## Migration Guide

### For Existing Code Using JSON Storage

**Before (JSON files):**
```python
from controllers.data.history import save_history, get_history

# Save (synchronous)
save_history(user_id, history_id, session_id, query, answer, feedback, feedback_status, references, chart)

# Get (synchronous)  
history = get_history(user_id, session_id)
```

**After (MongoDB):**
```python
from controllers.data.history import save_history_mongodb, get_history_mongodb

# Save (asynchronous)
result = await save_history_mongodb(user_id, history_id, session_id, query, answer, feedback, feedback_status, references, chart)

# Get (asynchronous)
history = await get_history_mongodb(user_id, session_id)
```

## Benefits of MongoDB Implementation

1. **Performance**: Queries nhanh hơn với proper indexing
2. **Scalability**: Có thể handle millions of records
3. **Reliability**: Không bị lỗi file system
4. **Concurrent Access**: Nhiều users có thể truy cập đồng thời
5. **Backup & Recovery**: Dễ dàng backup và restore
6. **Search Capabilities**: Có thể search và filter dễ dàng

## Configuration

Đảm bảo MongoDB connection string đã được cấu hình trong `.env`:
```
MONGODB_HOST=144.91.113.233
MONGODB_PORT=27017
MONGODB_DATABASE="mekongai_content_creator"
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_password
MONGODB_CONNECTION="mongodb://admin:your_password@144.91.113.233:27017/mekongai_content_creator?authSource=admin"
```

## Testing

Chạy test script để kiểm tra implementation:
```bash
python test_mongodb_simple.py
```

## Cleanup Functions

MongoDBManager cũng cung cấp cleanup function để xóa history cũ:
```python
from controllers.databases.nosql.mongodb import mongodb_manager

# Xóa history cũ hơn 30 ngày
deleted_count = await mongodb_manager.cleanup_old_history(keep_days=30)
```