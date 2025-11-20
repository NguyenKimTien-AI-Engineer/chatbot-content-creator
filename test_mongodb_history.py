#!/usr/bin/env python3
"""
Test script cho MongoDB history functions.
"""

import asyncio
import uuid
from datetime import datetime
from controllers.databases.nosql.mongodb import mongodb_manager
from controllers.data.history import (
    save_history_mongodb,
    get_history_mongodb,
    get_all_history_user_mongodb,
    update_feedback_mongodb,
    get_history_context_mongodb_v1,
    get_history_context_v2_mongodb
)


async def test_mongodb_connection():
    """Test kết nối MongoDB."""
    print("Testing MongoDB connection...")
    success = await mongodb_manager.connect()
    if success:
        print("✅ MongoDB connected successfully!")
        return True
    else:
        print("❌ MongoDB connection failed!")
        return False


async def test_save_history():
    """Test lưu history vào MongoDB."""
    print("\nTesting save_history_mongodb...")
    
    user_id = "test_user_001"
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    history_id = str(uuid.uuid4())
    
    result = await save_history_mongodb(
        user_id=user_id,
        history_id=history_id,
        session_id=session_id,
        query="Xin chào, bạn có thể giúp tôi tạo content không?",
        answer="Chào bạn! Tôi có thể giúp bạn tạo content. Bạn muốn tạo content về chủ đề gì?",
        feedback="",
        feedback_status="",
        references=["ref1", "ref2"],
        chart=None
    )
    
    if result:
        print(f"✅ History saved successfully! ID: {result}")
        return history_id, session_id, user_id
    else:
        print("❌ Failed to save history!")
        return None, None, None


async def test_get_history(user_id: str, session_id: str):
    """Test lấy history từ MongoDB."""
    print(f"\nTesting get_history_mongodb for user: {user_id}, session: {session_id}")
    
    history = await get_history_mongodb(user_id, session_id)
    
    if history:
        print(f"✅ Found {len(history)} history entries!")
        for entry in history:
            print(f"  - Query: {entry.get('query', 'N/A')}")
            print(f"  - Answer: {entry.get('answer', 'N/A')[:50]}...")
        return True
    else:
        print("❌ No history found!")
        return False


async def test_update_feedback(user_id: str, history_id: str):
    """Test cập nhật feedback."""
    print(f"\nTesting update_feedback_mongodb for history: {history_id}")
    
    success, updated_entries = await update_feedback_mongodb(
        user_id=user_id,
        history_id=history_id,
        new_feedback="Rất tốt!",
        new_feedback_status="positive"
    )
    
    if success:
        print("✅ Feedback updated successfully!")
        print(f"  - Updated entries: {len(updated_entries)}")
        for entry in updated_entries:
            print(f"  - Feedback: {entry.get('feedback')}")
            print(f"  - Status: {entry.get('feedback_status')}")
        return True
    else:
        print("❌ Failed to update feedback!")
        return False


async def test_get_all_history(user_id: str):
    """Test lấy tất cả history của user."""
    print(f"\nTesting get_all_history_user_mongodb for user: {user_id}")
    
    histories = await get_all_history_user_mongodb(user_id)
    
    if histories:
        print(f"✅ Found {len(histories)} sessions!")
        for i, session in enumerate(histories):
            print(f"  - Session {i+1}: {len(session)} entries")
        return True
    else:
        print("❌ No history found!")
        return False


async def test_history_context(user_id: str, session_id: str):
    """Test lấy history context."""
    print(f"\nTesting get_history_context_mongodb_v1 for user: {user_id}, session: {session_id}")
    
    context = await get_history_context_mongodb_v1(
        user_id=user_id,
        query="Tôi muốn tạo content về thời trang",
        session_id=session_id
    )
    
    if context:
        print("✅ History context generated successfully!")
        print(f"  - Context length: {len(context)} characters")
        print(f"  - Preview: {context[:100]}...")
        return True
    else:
        print("❌ Failed to generate history context!")
        return False


async def test_cleanup():
    """Test cleanup old history."""
    print("\nTesting cleanup_old_history...")
    
    deleted_count = await mongodb_manager.cleanup_old_history(keep_days=7)
    print(f"✅ Cleaned up {deleted_count} old history entries!")
    return True


async def main():
    """Main test function."""
    print("🚀 Starting MongoDB History Tests")
    print("=" * 50)
    
    # Test kết nối
    if not await test_mongodb_connection():
        return
    
    # Test save history
    history_id, session_id, user_id = await test_save_history()
    if not history_id:
        return
    
    # Test get history
    await test_get_history(user_id, session_id)
    
    # Test update feedback
    await test_update_feedback(user_id, history_id)
    
    # Test get all history
    await test_get_all_history(user_id)
    
    # Test history context
    await test_history_context(user_id, session_id)
    
    # Test cleanup (chạy cuối cùng)
    # await test_cleanup()  # Comment out để không xóa test data
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    
    # Cleanup connection
    await mongodb_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())