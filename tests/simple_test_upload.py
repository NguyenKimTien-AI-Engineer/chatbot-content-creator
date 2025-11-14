import requests
import os
from pathlib import Path


def test_simple_upload():
    """
    Test đơn giản: Upload PDF file và lưu collection với tên theo filename.
    """
    
    # Đường dẫn file PDF
    pdf_path = "d:/Document/Python_project/mekongai-content-creator/test_api_table.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ File không tồn tại: {pdf_path}")
        return
    
    filename = os.path.basename(pdf_path)
    
    print(f"🚀 Đang upload file: {filename}")
    print("-" * 50)
    
    # Bước 1: Upload file qua API
    upload_url = "http://localhost:1953/api/v1/upload-files"
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (filename, f, 'application/pdf')}
        data = {
            'user_id': 'test_user',
            'note': 'Test upload PDF',
            'language': 'vie+eng'
        }
        
        try:
            response = requests.post(upload_url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload thành công!")
                print(f"📨 Message: {result.get('message')}")
                
                # Lấy thông tin từ kết quả upload
                upload_data = result.get('data', {})
                if upload_data and isinstance(upload_data, dict):
                    print(f"📁 Collection được tạo: {upload_data.get('collection_name', 'Không có thông tin')}")
                elif isinstance(upload_data, list) and len(upload_data) > 0:
                    # Nếu data là list, lấy item đầu tiên
                    first_item = upload_data[0]
                    if isinstance(first_item, dict):
                        print(f"📁 Collection được tạo: {first_item.get('collection_name', 'Không có thông tin')}")
                else:
                    print(f"📁 Thông tin collection: {upload_data}")
                
            else:
                print(f"❌ Upload thất bại!")
                print(f"📊 Status: {response.status_code}")
                print(f"📨 Response: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Lỗi khi upload: {e}")
            return
    
    print("\n" + "-" * 50)
    
    # Bước 2: Lưu collection với tên theo filename
    print(f"🔄 Đang lưu collection với tên theo filename...")
    
    # Tạo collection name từ filename
    filename_without_ext = Path(filename).stem
    collection_name = filename_without_ext.replace(" ", "_").replace("-", "_")
    collection_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in collection_name)
    collection_name = '_'.join(filter(None, collection_name.split('_')))
    
    save_collection_url = "http://localhost:1953/api/v1/qdrant/collections/user"
    
    collection_data = {
        "user_id": "test_user",
        "info": {
            "collection_name": collection_name,
            "file_name": filename,
            "note": f"Collection cho file: {filename}"
        }
    }
    
    try:
        response = requests.post(save_collection_url, json=collection_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lưu collection thành công!")
            print(f"📁 Collection name: {collection_name}")
            print(f"📨 Message: {result.get('message')}")
        else:
            print(f"❌ Lưu collection thất bại!")
            print(f"📊 Status: {response.status_code}")
            print(f"📨 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi lưu collection: {e}")
    
    print("\n" + "-" * 50)
    
    # Bước 3: Kiểm tra danh sách collections
    print(f"📋 Kiểm tra danh sách collections...")
    
    get_collections_url = "http://localhost:1953/api/v1/qdrant/collections/user/test_user"
    
    try:
        response = requests.get(get_collections_url)
        
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
            print(f"❌ Lấy danh sách thất bại: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách collections: {e}")


if __name__ == "__main__":
    print("🎯 Test Upload PDF với Collection Name theo Filename")
    print("=" * 60)
    
    test_simple_upload()
    
    print("\n" + "=" * 60)
    print("✅ Hoàn thành test!")
    
    print("\n💡 Hướng dẫn:")
    print("1. Đảm bảo server đang chạy trên localhost:1953")
    print("2. File PDF nằm ở đúng đường dẫn")
    print("3. Kiểm tra Qdrant để xem collection đã được tạo chưa")