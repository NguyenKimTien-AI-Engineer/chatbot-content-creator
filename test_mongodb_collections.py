#!/usr/bin/env python3
"""
Test script để kiểm tra lưu history vào đúng collections histories và sessions.
"""

import asyncio
import uuid
import sys
import os

# Thêm path vào sys.path để import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.databases.nosql.mongodb import mongodb_manager


async def test_mongodb_collections():
    """Test lưu history vào đúng collections."""
    print("🚀 Testing MongoDB Collections - Histories & Sessions")
    print("=" * 60)
    
    try:
        # Test kết nối
        print("1. Testing MongoDB connection...")
        success = await mongodb_manager.connect()
        if success:
            print("✅ MongoDB connected successfully!")
            print(f"   Database: {mongodb_manager.database_name}")
        else:
            print("❌ MongoDB connection failed!")
            return False
        
        # Test save history
        print("\n2. Testing save_history into collections...")
        user_id = "test_user_collections"
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        history_id = str(uuid.uuid4())
        
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   History ID: {history_id}")
        
        result = await mongodb_manager.save_history(
            user_id=user_id,
            history_id=history_id,
            session_id=session_id,
            query="Test query for collections",
            answer="Test answer for collections",
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
        
        # Verify data in histories collection
        print("\n3. Verifying data in 'histories' collection...")
        history_data = await mongodb_manager.histories_collection.find_one({
            "history_id": history_id,
            "user_id": user_id,
            "session_id": session_id
        })
        
        if history_data:
            print("✅ History found in 'histories' collection!")
            print(f"   - Query: {history_data.get('query')}")
            print(f"   - Answer: {history_data.get('answer')}")
            print(f"   - User ID: {history_data.get('user_id')}")
            print(f"   - Session ID: {history_data.get('session_id')}")
        else:
            print("❌ History NOT found in 'histories' collection!")
            return False
        
        # Verify data in sessions collection
        print("\n4. Verifying data in 'sessions' collection...")
        session_data = await mongodb_manager.sessions_collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if session_data:
            print("✅ Session found in 'sessions' collection!")
            print(f"   - Session ID: {session_data.get('session_id')}")
            print(f"   - User ID: {session_data.get('user_id')}")
            print(f"   - Last Activity: {session_data.get('last_activity')}")
        else:
            print("❌ Session NOT found in 'sessions' collection!")
            return False
        
        # Test get_history function
        print("\n5. Testing get_history function...")
        history_list = await mongodb_manager.get_history(user_id, session_id)
        
        if history_list and len(history_list) > 0:
            print(f"✅ Retrieved {len(history_list)} history entries!")
            for i, entry in enumerate(history_list):
                print(f"   Entry {i+1}: {entry.get('query')}")
        else:
            print("❌ No history retrieved!")
            return False
        
        # Test get_user_sessions function
        print("\n6. Testing get_user_sessions function...")
        sessions = await mongodb_manager.get_user_sessions(user_id)
        
        if sessions and len(sessions) > 0:
            print(f"✅ Retrieved {len(sessions)} sessions!")
            for i, session in enumerate(sessions):
                print(f"   Session {i+1}: {session.get('session_id')}")
        else:
            print("❌ No sessions retrieved!")
            return False
        
        # Test get_session_info function
        print("\n7. Testing get_session_info function...")
        session_info = await mongodb_manager.get_session_info(session_id)
        
        if session_info:
            print("✅ Session info retrieved successfully!")
            print(f"   - Session ID: {session_info.get('session_id')}")
            print(f"   - User ID: {session_info.get('user_id')}")
        else:
            print("❌ Session info not retrieved!")
            return False
        
        # Test multiple histories in same session
        print("\n8. Testing multiple histories in same session...")
        history_id2 = str(uuid.uuid4())
        
        result2 = await mongodb_manager.save_history(
            user_id=user_id,
            history_id=history_id2,
            session_id=session_id,
            query="Second test query",
            answer="Second test answer",
            feedback="positive",
            feedback_status="good",
            references=["ref3"],
            chart=None
        )
        
        if result2:
            print(f"✅ Second history saved! ID: {result2}")
            
            # Check both histories
            all_history = await mongodb_manager.get_history(user_id, session_id)
            print(f"   Total histories in session: {len(all_history)}")
            
            if len(all_history) == 2:
                print("✅ Both histories found in same session!")
            else:
                print(f"❌ Expected 2 histories, found {len(all_history)}")
                return False
        else:
            print("❌ Failed to save second history!")
            return False
        
        # Test cleanup (optional - comment out to keep test data)
        # print("\n9. Testing cleanup...")
        # deleted = await mongodb_manager.delete_session(user_id, session_id)
        # if deleted:
        #     print("✅ Session and history cleaned up successfully!")
        # else:
        #     print("❌ Cleanup failed!")
        
        print("\n" + "=" * 60)
        print("✅ All collection tests completed successfully!")
        print("✅ Data is correctly saved to 'histories' and 'sessions' collections!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup connection
        await mongodb_manager.disconnect()
        print("\n🔌 MongoDB connection closed.")


if __name__ == "__main__":
    success = asyncio.run(test_mongodb_collections())
    if success:
        print("\n🎉 SUCCESS: All tests passed!")
    else:
        print("\n💥 FAILURE: Some tests failed!")
        sys.exit(1)