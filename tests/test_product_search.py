import asyncio
import httpx
import json

async def test_product_search():
    """Test the new product search functionality"""
    
    # Test the new Qdrant search endpoint
    url = "http://localhost:8000/api/v1/search-products-qdrant"
    
    payload = {
        "user_id": "test_user",
        "query": "Jen mini màu đen",
        "limit": 5
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Qdrant search successful!")
                print(f"Found {len(data.get('data', []))} products")
                for i, product in enumerate(data.get('data', []))):
                    print(f"Product {i+1}: {product}")
            else:
                print(f"❌ Qdrant search failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing Qdrant search: {e}")

    # Test the product name detection function
    print("\n--- Testing Product Name Detection ---")
    
    from bot.v1.chatbot_custom_prompt import extract_product_names_from_query
    
    test_queries = [
        "Jen mini màu đen",
        "Túi tote nữ",
        "Ví dài da bò",
        "Balo thời trang",
        "Túi xách da thật"
    ]
    
    for query in test_queries:
        product_names = extract_product_names_from_query(query)
        print(f"Query: '{query}' -> Detected products: {product_names}")

if __name__ == "__main__":
    asyncio.run(test_product_search())