#!/usr/bin/env python3
"""
Test script to verify product name detection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.v1.chatbot_custom_prompt import extract_product_names_from_query

def test_product_detection():
    """Test the product name detection function"""
    
    test_queries = [
        "Jen mini màu đen",
        "Túi tote nữ",
        "Ví dài da bò", 
        "Balo thời trang",
        "Túi xách da thật",
        "Ví cầm tay nữ",
        "Túi crossbody nhỏ",
        "Ví kéo khóa",
        "Túi đeo chéo",
        "Ví nữ thời trang",
        "Jen mini",
        "Tote bag",
        "Crossbody ví",
        "Túi tote crossbody",
        "Ví dài nữ"
    ]
    
    print("🧪 Testing Product Name Detection")
    print("=" * 50)
    
    for query in test_queries:
        product_names = extract_product_names_from_query(query)
        status = "✅" if product_names else "❌"
        print(f"{status} Query: '{query}' -> Detected: {product_names}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_product_detection()