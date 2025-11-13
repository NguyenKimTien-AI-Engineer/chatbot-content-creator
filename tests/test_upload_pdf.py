import asyncio
import aiofiles
import requests
import os
from pathlib import Path


async def test_upload_pdf_to_qdrant():
    """
    Test upload PDF file to Qdrant collection using the API endpoint.
    The collection name will be automatically generated based on filename.
    """
    
    # API endpoint
    api_url = "http://localhost:1945/api/v1/upload-files"
    
    # Path to the PDF file
    pdf_path = Path("d:/Document/Python_project/mekongai-content-creator/Fanpage Content Agent Prompts Configuration.pdf")
    
    if not pdf_path.exists():
        print(f"❌ File không tồn tại: {pdf_path}")
        return
    
    # Đọc file PDF
    async with aiofiles.open(pdf_path, 'rb') as f:
        file_content = await f.read()
    
    # Chuẩn bị dữ liệu upload
    files = {
        'file': ('Fanpage Content Agent Prompts Configuration.pdf', file_content, 'application/pdf')
    }
    
    # Chuẩn bị form data
    data = {
        'user_id': 'test_user_001',
        'note': 'Test upload PDF file với collection name theo tên file',
        'language': 'vie+eng'
    }
    
    try:
        print(f"📤 Đang upload file: {pdf_path.name}")
        print(f"📋 User ID: test_user_001")
        print(f"📝 Note: {data['note']}")
        
        # Gửi request upload
        response = requests.post(api_url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload thành công!")
            print(f"📊 Status: {result.get('status')}")
            print(f"💾 Data: {result.get('data')}")
            print(f"📨 Message: {result.get('message')}")
            
            # Collection name sẽ được tạo tự động theo format: {CHATBOT_NAME}_{user_id}_{uuid}
            # Trong đó uuid được sinh ra ngẫu nhiên cho mỗi upload
            
        else:
            print(f"❌ Upload thất bại!")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📨 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi upload: {e}")


async def test_upload_with_custom_collection_name():
    """
    Test upload và lưu với collection name tùy chỉnh theo tên file.
    Sử dụng endpoint save collection để tạo collection với tên theo ý muốn.
    """
    
    # Trước tiên upload file như bình thường
    await test_upload_pdf_to_qdrant()
    
    # Sau đó có thể sử dụng endpoint save collection để lưu với tên tùy chỉnh
    api_save_collection = "http://localhost:1945/api/v1/qdrant/collections/user"
    
    collection_data = {
        "user_id": "test_user_001",
        "info": {
            "collection_name": "Fanpage_Content_Agent_Prompts_Configuration",  # Tên theo filename
            "file_name": "Fanpage Content Agent Prompts Configuration.pdf",
            "note": "Collection với tên theo filename"
        }
    }
    
    try:
        print(f"\n💾 Đang lưu collection với tên tùy chỉnh...")
        response = requests.post(api_save_collection, json=collection_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lưu collection thành công!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📨 Message: {result.get('message')}")
            print(f"💾 Data: {result.get('data')}")
        else:
            print(f"❌ Lưu collection thất bại!")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📨 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi lưu collection: {e}")


async def test_get_user_collections():
    """
    Test lấy danh sách collections của user để kiểm tra.
    """
    
    api_get_collections = "http://localhost:1945/api/v1/qdrant/collections/user/test_user_001"
    
    try:
        print(f"\n📋 Đang lấy danh sách collections...")
        response = requests.get(api_get_collections)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lấy danh sách thành công!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📨 Message: {result.get('message')}")
            
            collections = result.get('data', [])
            if collections:
                print(f"📁 Có {len(collections)} collections:")
                for i, collection in enumerate(collections, 1):
                    print(f"  {i}. Collection: {collection.get('collection_name')}")
                    print(f"     File: {collection.get('file_name')}")
                    print(f"     Note: {collection.get('note')}")
            else:
                print("📁 Không có collections nào.")
        else:
            print(f"❌ Lấy danh sách thất bại!")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📨 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách collections: {e}")


async def main():
    """
    Main test function.
    """
    print("🚀 Bắt đầu test upload PDF to Qdrant")
    print("=" * 50)
    
    # Test 1: Upload file PDF
    await test_upload_pdf_to_qdrant()
    
    print("\n" + "=" * 50)
    
    # Test 2: Lưu collection với tên tùy chỉnh
    await test_upload_with_custom_collection_name()
    
    print("\n" + "=" * 50)
    
    # Test 3: Kiểm tra danh sách collections
    await test_get_user_collections()
    
    print("\n" + "=" * 50)
    print("✅ Hoàn thành test upload PDF to Qdrant")


if __name__ == "__main__":
    # Chạy test
    asyncio.run(main())