import asyncio
import aiofiles
import requests
import os
import uuid
from pathlib import Path
import json


async def upload_pdf_with_filename_as_collection():
    """
    Upload PDF và lưu với collection name theo tên file.
    Sử dụng 2 bước:
    1. Upload file qua API upload-files
    2. Lưu collection với tên theo filename qua API save collection
    """
    
    # Đường dẫn file PDF
    pdf_path = Path("d:/Document/Python_project/mekongai-content-creator/Fanpage Content Agent Prompts Configuration.pdf")
    
    if not pdf_path.exists():
        print(f"❌ File không tồn tại: {pdf_path}")
        return
    
    # Đọc file PDF
    async with aiofiles.open(pdf_path, 'rb') as f:
        file_content = await f.read()
    
    # Bước 1: Upload file
    print("🔄 Bước 1: Upload file PDF...")
    
    upload_url = "http://localhost:1945/api/v1/upload-files"
    
    files = {
        'file': (pdf_path.name, file_content, 'application/pdf')
    }
    
    upload_data = {
        'user_id': 'test_user_filename',
        'note': 'Upload PDF để lưu với collection name theo tên file',
        'language': 'vie+eng'
    }
    
    try:
        response = requests.post(upload_url, files=files, data=upload_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload thành công!")
            
            # Lấy thông tin từ kết quả upload
            upload_data_result = result.get('data', {})
            if isinstance(upload_data_result, dict):
                # Có thể có collection name từ upload
                original_collection = upload_data_result.get('collection_name', '')
                print(f"📁 Collection name từ upload: {original_collection}")
            
        else:
            print(f"❌ Upload thất bại: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Lỗi khi upload: {e}")
        return
    
    # Bước 2: Lưu collection với tên theo filename
    print(f"\n🔄 Bước 2: Lưu collection với tên theo filename...")
    
    # Tạo collection name từ filename (loại bỏ ký tự đặc biệt và spaces)
    filename_without_ext = pdf_path.stem  # Lấy tên file không có extension
    # Thay thế spaces và ký tự đặc biệt bằng underscore
    collection_name = filename_without_ext.replace(" ", "_").replace("-", "_").replace(".", "_")
    # Loại bỏ các ký tự không hợp lệ
    collection_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in collection_name)
    # Loại bỏ underscore thừa
    collection_name = '_'.join(filter(None, collection_name.split('_')))
    
    print(f"📁 Collection name theo filename: {collection_name}")
    
    save_collection_url = "http://localhost:1945/api/v1/qdrant/collections/user"
    
    collection_data = {
        "user_id": "test_user_filename",
        "info": {
            "collection_name": collection_name,
            "file_name": pdf_path.name,
            "note": f"Collection được đặt tên theo filename: {pdf_path.name}"
        }
    }
    
    try:
        response = requests.post(save_collection_url, json=collection_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lưu collection thành công!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📨 Message: {result.get('message')}")
            print(f"💾 Data: {json.dumps(result.get('data'), indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Lưu collection thất bại: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi lưu collection: {e}")


async def test_multiple_files_with_filename_collections():
    """
    Test upload nhiều file và đặt tên collection theo tên file.
    """
    
    # Danh sách file để test (có thể thêm nhiều file)
    test_files = [
        "d:/Document/Python_project/mekongai-content-creator/Fanpage Content Agent Prompts Configuration.pdf",
        # Có thể thêm các file khác ở đây
    ]
    
    for file_path in test_files:
        pdf_path = Path(file_path)
        
        if not pdf_path.exists():
            print(f"❌ File không tồn tại: {pdf_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"🔄 Đang xử lý file: {pdf_path.name}")
        
        # Upload file
        async with aiofiles.open(pdf_path, 'rb') as f:
            file_content = await f.read()
        
        upload_url = "http://localhost:1945/api/v1/upload-files"
        
        files = {
            'file': (pdf_path.name, file_content, 'application/pdf')
        }
        
        upload_data = {
            'user_id': 'test_user_multiple',
            'note': f'Test upload {pdf_path.name}',
            'language': 'vie+eng'
        }
        
        try:
            response = requests.post(upload_url, files=files, data=upload_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload thành công!")
                
                # Lấy collection name từ filename
                filename_without_ext = pdf_path.stem
                collection_name = filename_without_ext.replace(" ", "_").replace("-", "_").replace(".", "_")
                collection_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in collection_name)
                collection_name = '_'.join(filter(None, collection_name.split('_')))
                
                print(f"📁 Collection name: {collection_name}")
                
                # Lưu collection với tên theo filename
                save_collection_url = "http://localhost:1945/api/v1/qdrant/collections/user"
                
                collection_data = {
                    "user_id": "test_user_multiple",
                    "info": {
                        "collection_name": collection_name,
                        "file_name": pdf_path.name,
                        "note": f"Collection cho file: {pdf_path.name}"
                    }
                }
                
                save_response = requests.post(save_collection_url, json=collection_data)
                
                if save_response.status_code == 200:
                    print(f"✅ Lưu collection thành công!")
                else:
                    print(f"❌ Lưu collection thất bại: {save_response.text}")
                    
            else:
                print(f"❌ Upload thất bại: {response.text}")
                
        except Exception as e:
            print(f"❌ Lỗi khi xử lý file {pdf_path.name}: {e}")


async def get_collections_info():
    """
    Lấy thông tin các collections để kiểm tra.
    """
    
    api_urls = [
        "http://localhost:1945/api/v1/qdrant/collections/user/test_user_filename",
        "http://localhost:1945/api/v1/qdrant/collections/user/test_user_multiple"
    ]
    
    for url in api_urls:
        user_id = url.split('/')[-1]
        print(f"\n📋 Collections cho user: {user_id}")
        print("-" * 40)
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
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
                print(f"❌ Lỗi khi lấy collections: {response.text}")
                
        except Exception as e:
            print(f"❌ Lỗi khi lấy collections: {e}")


async def main():
    """
    Main test function.
    """
    print("🚀 Bắt đầu test upload PDF với collection name theo filename")
    print("=" * 60)
    
    # Test 1: Upload single file với collection name theo filename
    await upload_pdf_with_filename_as_collection()
    
    print("\n" + "=" * 60)
    
    # Test 2: Upload multiple files (có thể mở rộng)
    # await test_multiple_files_with_filename_collections()
    
    print("\n" + "=" * 60)
    
    # Test 3: Kiểm tra collections
    await get_collections_info()
    
    print("\n" + "=" * 60)
    print("✅ Hoàn thành test upload PDF với collection name theo filename")


if __name__ == "__main__":
    # Chạy test
    asyncio.run(main())