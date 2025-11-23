#!/usr/bin/env python3
"""
Script để kiểm tra cấu trúc collections trong MongoDB.
"""

import asyncio
import sys
import os

# Thêm path vào sys.path để import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.databases.nosql.mongodb import mongodb_manager


async def check_collections_structure():
    """Kiểm tra cấu trúc collections trong database."""
    print("🔍 Checking MongoDB Collections Structure")
    print("=" * 50)
    
    try:
        # Test kết nối
        success = await mongodb_manager.connect()
        if success:
            print("✅ MongoDB connected successfully!")
        else:
            print("❌ MongoDB connection failed!")
            return False
        
        # Lấy danh sách collections
        print("\n📋 Database Collections:")
        collections = await mongodb_manager.database.list_collection_names()
        
        for collection_name in collections:
            print(f"\n📊 Collection: {collection_name}")
            
            # Đếm số documents
            collection = mongodb_manager.database[collection_name]
            count = await collection.count_documents({})
            print(f"   Documents count: {count}")
            
            # Lấy một document mẫu nếu có
            if count > 0:
                sample_doc = await collection.find_one({})
                if sample_doc:
                    sample_doc.pop("_id", None)  # Remove MongoDB internal ID
                    print(f"   Sample document keys: {list(sample_doc.keys())}")
                    
                    # Hiển thị một phần dữ liệu mẫu
                    print("   Sample data:")
                    for key, value in list(sample_doc.items())[:3]:  # Chỉ hiển thị 3 field đầu
                        if isinstance(value, str) and len(value) > 50:
                            print(f"     {key}: {value[:50]}...")
                        else:
                            print(f"     {key}: {value}")
                    if len(sample_doc) > 3:
                        print(f"     ... và {len(sample_doc) - 3} fields khác")
        
        # Kiểm tra indexes của collections chính
        print("\n🔑 Collection Indexes:")
        
        important_collections = ["histories", "sessions", "templates", "products"]
        
        for collection_name in important_collections:
            if collection_name in collections:
                print(f"\n📋 {collection_name} indexes:")
                collection = mongodb_manager.database[collection_name]
                indexes = await collection.list_indexes().to_list(None)
                
                for index in indexes:
                    index_name = index.get("name", "unknown")
                    index_keys = index.get("key", {})
                    unique = index.get("unique", False)
                    
                    key_str = ", ".join([f"{k}:{v}" for k, v in index_keys.items()])
                    unique_str = " (UNIQUE)" if unique else ""
                    print(f"   - {index_name}: {key_str}{unique_str}")
        
        print("\n" + "=" * 50)
        print("✅ Collection structure check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking collections: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup connection
        await mongodb_manager.disconnect()
        print("\n🔌 MongoDB connection closed.")


if __name__ == "__main__":
    success = asyncio.run(check_collections_structure())
    if success:
        print("\n🎉 SUCCESS: Collections structure verified!")
    else:
        print("\n💥 FAILURE: Could not verify collections!")
        sys.exit(1)