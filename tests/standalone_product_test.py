#!/usr/bin/env python3
"""
Standalone test for product name detection
"""

import re

def extract_product_names_from_query(query):
    """Extract product names from user query using keyword matching"""
    
    # Define product keywords to detect
    product_keywords = [
        "túi", "ví", "balo", "tote", "crossbody", "clutch", 
        "backpack", "handbag", "wallet", "purse", "bag",
        "jen", "mini", "nano", "micro", "maxi", "medium",
        "da", "canvas", "vải", "leather", "fabric"
    ]
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    # Find matching keywords
    detected_keywords = []
    for keyword in product_keywords:
        if keyword in query_lower:
            detected_keywords.append(keyword)
    
    # Additional pattern matching for specific product names
    patterns = [
        r'jen\s+\w+',  # Matches "jen mini", "jen nano", etc.
        r'túi\s+\w+',  # Matches "túi tote", "túi crossbody", etc.
        r'ví\s+\w+',   # Matches "ví dài", "ví ngắn", etc.
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, query_lower)
        detected_keywords.extend(matches)
    
    # Remove duplicates and return
    return list(set(detected_keywords))

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