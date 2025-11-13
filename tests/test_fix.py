#!/usr/bin/env python3
"""
Test script để kiểm tra lỗi prompt template đã được sửa chưa
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.v1.chatbot_custom_prompt import chatbot_custom_prompt

def test_prompt_fix():
    """Test xem prompt template có hoạt động đúng không"""
    try:
        # Test với query có chứa tên sản phẩm
        user_id = "test_user"
        query = "có túi Jen mini màu đen màu đen không"
        collections = ["default"]
        session_id = "test_session"
        history_id = "test_history"
        
        print(f"Testing query: {query}")
        
        # Gọi hàm chatbot_custom_prompt với include_products=True
        answer, references = chatbot_custom_prompt(
            user_id=user_id,
            query=query,
            collections=collections,
            session_id=session_id,
            history_id=history_id,
            include_products=True
        )
        
        print("✅ Test thành công!")
        print(f"Answer length: {len(answer)} characters")
        print(f"First 200 chars: {answer[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test thất bại: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prompt_fix()
    sys.exit(0 if success else 1)