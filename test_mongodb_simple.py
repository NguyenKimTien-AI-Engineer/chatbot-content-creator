#!/usr/bin/env python3
"""
Test script đơn giản cho MongoDB history functions.
"""

import asyncio
import uuid
import sys
import os

# Thêm path vào sys.path để import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.databases.nosql.mongodb import mongodb_manager


async def test_mongodb_basic():
    """Test cơ bản MongoDB connection và history functions."""
    print("🚀 Testing MongoDB History Functions")
    print("=" * 50)
    
    try:
        # Test kết nối
        print("1. Testing MongoDB connection...")
        success = await mongodb_manager.connect()
        if success:
            print("✅ MongoDB connected successfully!")
        else:
            print("❌ MongoDB connection failed!")
            return False
        
        # Test save history
        print("\n2. Testing save_history...")
        user_id = "test_user_001"
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        history_id = str(uuid.uuid4())
        
        result = await mongodb_manager.save_history(
            user_id=user_id,
            history_id=history_id,
            session_id=session_id,
            query="Xin chào, bạn có thể giúp tôi tạo content không?",
            answer="Chào bạn! Tôi có thể giúp bạn tạo content.",
            feedback="",
            feedback_status="",
            references=["ref1", "ref2"],
            chart=None
        )
        
        if result:
            print(f"✅ History saved successfully! ID: {result}")
        else:
            print("❌ Failed to save history!")
            return False
        
        # Test get history
        print(f"\n3. Testing get_history for session: {session_id}")
        history = await mongodb_manager.get_history(user_id, session_id)
        
        if history:
            print(f"✅ Found {len(history)} history entries!")
            for entry in history:
                print(f"  - Query: {entry.get('query', 'N/A')}")
                print(f"  - Answer: {entry.get('answer', 'N/A')[:50]}...")
        else:
            print("❌ No history found!")
            return False
        
        # Test update feedback
        print(f"\n4. Testing update_feedback for history: {history_id}")
        success, updated_entries = await mongodb_manager.update_feedback(
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
        else:
            print("❌ Failed to update feedback!")
            return False
        
        # Test get all history
        print(f"\n5. Testing get_all_history_user for user: {user_id}")
        histories = await mongodb_manager.get_all_history_user(user_id)
        
        if histories:
            print(f"✅ Found {len(histories)} sessions!")
            for i, session in enumerate(histories):
                print(f"  - Session {i+1}: {len(session)} entries")
        else:
            print("❌ No history found!")
            return False
        
        # Test history context
        print(f"\n6. Testing get_history_context for user: {user_id}, session: {session_id}")
        context = await mongodb_manager.get_history_context(
            user_id=user_id,
            query="Tôi muốn tạo content về thời trang",
            session_id=session_id
        )
        
        if context:
            print("✅ History context generated successfully!")
            print(f"  - Context length: {len(context)} characters")
            print(f"  - Preview: {context[:100]}...")
        else:
            print("❌ Failed to generate history context!")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All MongoDB tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        # Cleanup connection
        await mongodb_manager.disconnect()
        print("\n🔌 MongoDB connection closed.")


if __name__ == "__main__":
    asyncio.run(test_mongodb_basic())