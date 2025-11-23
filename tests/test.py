import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

# Cấu hình
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_SERVER = os.getenv("QDRANT_SERVER")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Đường dẫn file dữ liệu
DATA_FILE_PATH = r"D:\Document\Python_project\mekongai-content-creator\test_api_filtered.json"

COLLECTION_NAME = "kat_products"
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSION = 1536

# Khởi tạo clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Khởi tạo Qdrant client
if QDRANT_SERVER:
    # Sử dụng Qdrant Cloud
    qdrant_client = QdrantClient(
        url=QDRANT_SERVER,
        api_key=QDRANT_API_KEY,
        timeout=120  # Tăng timeout lên 120 giây
    )
else:
    # Sử dụng Qdrant local
    qdrant_client = QdrantClient(
        host=QDRANT_HOST,
        port=int(QDRANT_PORT) if QDRANT_PORT else 6333,
        timeout=120  # Tăng timeout lên 120 giây
    )


def load_products_from_json(file_path: str) -> List[Dict[str, str]]:
    """
    Đọc dữ liệu sản phẩm từ file JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Đã đọc {len(data)} sản phẩm từ file: {file_path}")
        return data
    except FileNotFoundError:
        print(f"✗ Không tìm thấy file: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Lỗi khi parse JSON: {e}")
        raise
    except Exception as e:
        print(f"✗ Lỗi không xác định: {e}")
        raise


def create_product_embedding_data(product: Dict[str, str]) -> Dict:
    """
    Tạo dữ liệu embedding cho toàn bộ sản phẩm (không chunk)
    """
    name = product["name"]
    description = product["description"]
    
    # Kết hợp tên và toàn bộ description
    full_text = f"{name}\n\n{description}"
    
    return {
        "product_name": name,
        "text": full_text,
        "full_description": description
    }


def get_embedding(text: str) -> List[float]:
    """
    Lấy embedding từ OpenAI
    """
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Lỗi khi tạo embedding: {e}")
        return None


def create_collection():
    """
    Tạo collection trong Qdrant
    """
    try:
        # Xóa collection cũ nếu tồn tại
        collections = qdrant_client.get_collections().collections
        if any(c.name == COLLECTION_NAME for c in collections):
            print(f"Xóa collection cũ: {COLLECTION_NAME}")
            qdrant_client.delete_collection(COLLECTION_NAME)
        
        # Tạo collection mới
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
        print(f"✓ Đã tạo collection: {COLLECTION_NAME}")
    except Exception as e:
        print(f"Lỗi khi tạo collection: {e}")
        raise


def process_and_upload_products(products: List[Dict[str, str]]):
    """
    Xử lý và upload sản phẩm vào Qdrant (không chunk)
    """
    all_points = []
    
    print(f"\n{'='*60}")
    print(f"Bắt đầu xử lý {len(products)} sản phẩm...")
    print(f"Mỗi sản phẩm = 1 vector (không chia nhỏ)")
    print(f"{'='*60}\n")
    
    for idx, product in enumerate(products, 1):
        product_name = product["name"]
        print(f"[{idx}/{len(products)}] Đang xử lý: {product_name}")
        
        # Tạo dữ liệu embedding cho toàn bộ sản phẩm
        embedding_data = create_product_embedding_data(product)
        print(f"  → Độ dài text: {len(embedding_data['text'])} ký tự")
        
        # Tạo embedding
        embedding = get_embedding(embedding_data["text"])
        
        if embedding:
            point = PointStruct(
                id=idx - 1,  # ID từ 0
                vector=embedding,
                payload={
                    "product_name": embedding_data["product_name"],
                    "text": embedding_data["text"],
                    "full_description": embedding_data["full_description"],
                    "product_id": idx
                }
            )
            all_points.append(point)
            print(f"  → Embedding: ✓")
        else:
            print(f"  → Embedding: ✗ (lỗi)")
        
        print()
    
    # Upload tất cả points vào Qdrant
    if all_points:
        print(f"{'='*60}")
        print(f"Đang upload {len(all_points)} vectors vào Qdrant...")
        print(f"{'='*60}\n")
        
        # Upload theo batch để tránh timeout
        batch_size = 10  # Giảm batch size xuống 10 để tránh timeout
        for i in range(0, len(all_points), batch_size):
            batch = all_points[i:i + batch_size]
            try:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )
                print(f"✓ Đã upload batch {i//batch_size + 1}/{(len(all_points)-1)//batch_size + 1}")
            except Exception as e:
                print(f"✗ Lỗi upload batch {i//batch_size + 1}: {e}")
                # Thử lại với batch size nhỏ hơn
                if batch_size > 1:
                    print("Thử lại với batch size nhỏ hơn...")
                    smaller_batch_size = max(1, batch_size // 2)
                    for j in range(0, len(batch), smaller_batch_size):
                        smaller_batch = batch[j:j + smaller_batch_size]
                        qdrant_client.upsert(
                            collection_name=COLLECTION_NAME,
                            points=smaller_batch
                        )
                        print(f"  ✓ Đã upload sub-batch {j//smaller_batch_size + 1}")
                else:
                    raise
        
        print(f"\n✓ Hoàn thành! Đã upload {len(all_points)} vectors")
        print(f"✓ Mỗi sản phẩm = 1 vector với toàn bộ description")


def test_search(query: str, limit: int = 5):
    """
    Test tìm kiếm với một query
    """
    print(f"\n{'='*60}")
    print(f"TEST TÌM KIẾM: '{query}'")
    print(f"{'='*60}\n")
    
    # Tạo embedding cho query
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        print("Lỗi: Không thể tạo embedding cho query")
        return
    
    # Tìm kiếm trong Qdrant
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=limit
    )
    
    # Hiển thị kết quả
    for idx, result in enumerate(results, 1):
        print(f"[{idx}] Score: {result.score:.4f}")
        print(f"Sản phẩm: {result.payload['product_name']}")
        print(f"Text preview: {result.payload['text'][:200]}...")
        print(f"{'-'*60}\n")


def get_collection_info():
    """
    Hiển thị thông tin collection
    """
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        print(f"\n{'='*60}")
        print(f"THÔNG TIN COLLECTION")
        print(f"{'='*60}")
        print(f"Tên: {COLLECTION_NAME}")
        print(f"Số vectors: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print(f"Distance: {collection_info.config.params.vectors.distance}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"Lỗi khi lấy thông tin collection: {e}")


def main():
    """
    Hàm main chạy toàn bộ pipeline
    """
    try:
        # Bước 1: Đọc dữ liệu từ file JSON
        print(f"\n{'='*60}")
        print(f"BƯỚC 1: ĐỌC DỮ LIỆU")
        print(f"{'='*60}\n")
        
        products = load_products_from_json(DATA_FILE_PATH)
        
        # Bước 2: Tạo collection trong Qdrant
        print(f"\n{'='*60}")
        print(f"BƯỚC 2: TẠO COLLECTION")
        print(f"{'='*60}\n")
        
        create_collection()
        
        # Bước 3: Xử lý và upload sản phẩm
        print(f"\n{'='*60}")
        print(f"BƯỚC 3: XỬ LÝ VÀ UPLOAD")
        print(f"{'='*60}\n")
        
        process_and_upload_products(products)
        
        # Bước 4: Hiển thị thông tin collection
        get_collection_info()
        
        # Bước 5: Test tìm kiếm
        print(f"\n{'='*60}")
        print(f"BƯỚC 4: TEST TÌM KIẾM")
        print(f"{'='*60}\n")
        
        # Test với một số queries
        test_queries = [
            "Tôi muốn tìm ví đựng điện thoại màu đen",
            "Túi xách công sở cho nữ",
            "Ví mini nhỏ gọn màu hồng"
        ]
        
        for query in test_queries:
            test_search(query, limit=3)
        
        print(f"\n{'='*60}")
        print(f"✓ HOÀN THÀNH TẤT CẢ CÁC BƯỚC!")
        print(f"✓ Tổng số sản phẩm: {len(products)}")
        print(f"✓ Tổng số vectors: {len(products)}")
        print(f"✓ Mỗi sản phẩm = 1 vector (no chunking)")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ LỖI: {e}")
        raise


if __name__ == "__main__":
    main()
# Chunk_size = 500
# import os
# import json
# from typing import List, Dict
# from dotenv import load_dotenv
# from openai import OpenAI
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams, PointStruct
# from configs import constant

# # Load environment variables
# load_dotenv()

# # Cấu hình
# QDRANT_HOST = os.getenv("QDRANT_HOST")
# QDRANT_PORT = os.getenv("QDRANT_PORT")
# QDRANT_SERVER = os.getenv("QDRANT_SERVER")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Đường dẫn file dữ liệu
# DATA_FILE_PATH = r"D:\Document\Python_project\mekongai-content-creator\test_api_filtered.json"

# COLLECTION_NAME = "kat_products"
# EMBEDDING_MODEL = "text-embedding-ada-002"
# EMBEDDING_DIMENSION = 1536
# NODE_CHUNK_SIZE_TYPE_4 = 1024

# # Khởi tạo clients
# openai_client = OpenAI(api_key=OPENAI_API_KEY)

# # Khởi tạo Qdrant client
# if QDRANT_SERVER:
#     # Sử dụng Qdrant Cloud
#     qdrant_client = QdrantClient(
#         url=QDRANT_SERVER,
#         api_key=QDRANT_API_KEY
#     )
# else:
#     # Sử dụng Qdrant local
#     qdrant_client = QdrantClient(
#         host=QDRANT_HOST,
#         port=int(QDRANT_PORT) if QDRANT_PORT else 6333
#     )


# def load_products_from_json(file_path: str) -> List[Dict[str, str]]:
#     """
#     Đọc dữ liệu sản phẩm từ file JSON
#     """
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
        
#         print(f"✓ Đã đọc {len(data)} sản phẩm từ file: {file_path}")
#         return data
#     except FileNotFoundError:
#         print(f"✗ Không tìm thấy file: {file_path}")
#         raise
#     except json.JSONDecodeError as e:
#         print(f"✗ Lỗi khi parse JSON: {e}")
#         raise
#     except Exception as e:
#         print(f"✗ Lỗi không xác định: {e}")
#         raise


# def chunk_product_description(product: Dict[str, str], chunk_size: int = NODE_CHUNK_SIZE_TYPE_4) -> List[Dict]:
#     """
#     Chia description thành các chunks nhỏ hơn theo ngữ nghĩa
#     """
#     name = product["name"]
#     description = product["description"]
    
#     # Tách theo dấu xuống dòng và bullet points
#     paragraphs = [p.strip() for p in description.split('\n') if p.strip()]
    
#     chunks = []
#     current_chunk = ""
    
#     for para in paragraphs:
#         # Nếu chunk hiện tại + paragraph mới vượt quá chunk_size
#         if len(current_chunk) + len(para) > chunk_size and current_chunk:
#             chunks.append({
#                 "product_name": name,
#                 "text": f"{name}\n\n{current_chunk}",
#                 "chunk_type": "description"
#             })
#             current_chunk = para
#         else:
#             current_chunk += "\n\n" + para if current_chunk else para
    
#     # Thêm chunk cuối cùng
#     if current_chunk:
#         chunks.append({
#             "product_name": name,
#             "text": f"{name}\n\n{current_chunk}",
#             "chunk_type": "description"
#         })
    
#     # Luôn có một chunk tổng quan với tên + mô tả đầy đủ (hoặc 1000 ký tự đầu)
#     summary_text = f"{name}\n\n{description[:1000]}"
#     chunks.insert(0, {
#         "product_name": name,
#         "text": summary_text,
#         "chunk_type": "summary"
#     })
    
#     return chunks


# def get_embedding(text: str) -> List[float]:
#     """
#     Lấy embedding từ OpenAI
#     """
#     try:
#         response = openai_client.embeddings.create(
#             model=EMBEDDING_MODEL,
#             input=text
#         )
#         return response.data[0].embedding
#     except Exception as e:
#         print(f"Lỗi khi tạo embedding: {e}")
#         return None


# def create_collection():
#     """
#     Tạo collection trong Qdrant
#     """
#     try:
#         # Xóa collection cũ nếu tồn tại
#         collections = qdrant_client.get_collections().collections
#         if any(c.name == COLLECTION_NAME for c in collections):
#             print(f"Xóa collection cũ: {COLLECTION_NAME}")
#             qdrant_client.delete_collection(COLLECTION_NAME)
        
#         # Tạo collection mới
#         qdrant_client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(
#                 size=EMBEDDING_DIMENSION,
#                 distance=Distance.COSINE
#             )
#         )
#         print(f"✓ Đã tạo collection: {COLLECTION_NAME}")
#     except Exception as e:
#         print(f"Lỗi khi tạo collection: {e}")
#         raise


# def process_and_upload_products(products: List[Dict[str, str]]):
#     """
#     Xử lý và upload sản phẩm vào Qdrant
#     """
#     all_points = []
#     point_id = 0
    
#     print(f"\n{'='*60}")
#     print(f"Bắt đầu xử lý {len(products)} sản phẩm...")
#     print(f"{'='*60}\n")
    
#     for idx, product in enumerate(products, 1):
#         product_name = product["name"]
#         print(f"[{idx}/{len(products)}] Đang xử lý: {product_name}")
        
#         # Chunk description
#         chunks = chunk_product_description(product, chunk_size=500)
#         print(f"  → Tạo {len(chunks)} chunks")
        
#         # Tạo embedding cho mỗi chunk
#         for chunk_idx, chunk in enumerate(chunks, 1):
#             embedding = get_embedding(chunk["text"])
            
#             if embedding:
#                 point = PointStruct(
#                     id=point_id,
#                     vector=embedding,
#                     payload={
#                         "product_name": chunk["product_name"],
#                         "text": chunk["text"],
#                         "chunk_type": chunk["chunk_type"],
#                         "chunk_index": chunk_idx,
#                         "total_chunks": len(chunks),
#                         "full_description": product["description"]
#                     }
#                 )
#                 all_points.append(point)
#                 point_id += 1
#                 print(f"  → Chunk {chunk_idx}/{len(chunks)}: ✓")
#             else:
#                 print(f"  → Chunk {chunk_idx}/{len(chunks)}: ✗ (lỗi embedding)")
        
#         print()
    
#     # Upload tất cả points vào Qdrant
#     if all_points:
#         print(f"{'='*60}")
#         print(f"Đang upload {len(all_points)} vectors vào Qdrant...")
#         print(f"{'='*60}\n")
        
#         # Upload theo batch để tránh timeout
#         batch_size = 100
#         for i in range(0, len(all_points), batch_size):
#             batch = all_points[i:i + batch_size]
#             qdrant_client.upsert(
#                 collection_name=COLLECTION_NAME,
#                 points=batch
#             )
#             print(f"✓ Đã upload batch {i//batch_size + 1}/{(len(all_points)-1)//batch_size + 1}")
        
#         print(f"\n✓ Hoàn thành! Đã upload {len(all_points)} vectors")


# def test_search(query: str, limit: int = 5):
#     """
#     Test tìm kiếm với một query
#     """
#     print(f"\n{'='*60}")
#     print(f"TEST TÌM KIẾM: '{query}'")
#     print(f"{'='*60}\n")
    
#     # Tạo embedding cho query
#     query_embedding = get_embedding(query)
    
#     if not query_embedding:
#         print("Lỗi: Không thể tạo embedding cho query")
#         return
    
#     # Tìm kiếm trong Qdrant
#     results = qdrant_client.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=query_embedding,
#         limit=limit
#     )
    
#     # Hiển thị kết quả
#     for idx, result in enumerate(results, 1):
#         print(f"[{idx}] Score: {result.score:.4f}")
#         print(f"Sản phẩm: {result.payload['product_name']}")
#         print(f"Chunk type: {result.payload['chunk_type']}")
#         print(f"Text preview: {result.payload['text'][:150]}...")
#         print(f"{'-'*60}\n")


# def main():
#     """
#     Hàm main chạy toàn bộ pipeline
#     """
#     try:
#         # Bước 1: Đọc dữ liệu từ file JSON
#         print(f"\n{'='*60}")
#         print(f"BƯỚC 1: ĐỌC DỮ LIỆU")
#         print(f"{'='*60}\n")
        
#         products = load_products_from_json(DATA_FILE_PATH)
        
#         # Bước 2: Tạo collection trong Qdrant
#         print(f"\n{'='*60}")
#         print(f"BƯỚC 2: TẠO COLLECTION")
#         print(f"{'='*60}\n")
        
#         create_collection()
        
#         # Bước 3: Xử lý và upload sản phẩm
#         print(f"\n{'='*60}")
#         print(f"BƯỚC 3: XỬ LÝ VÀ UPLOAD")
#         print(f"{'='*60}\n")
        
#         process_and_upload_products(products)
        
#         # Bước 4: Test tìm kiếm
#         print(f"\n{'='*60}")
#         print(f"BƯỚC 4: TEST TÌM KIẾM")
#         print(f"{'='*60}\n")
        
#         # Test với một số queries
#         test_queries = [
#             "Tôi muốn tìm ví đựng điện thoại màu đen",
#             "Túi xách công sở cho nữ",
#             "Ví mini nhỏ gọn"
#         ]
        
#         for query in test_queries:
#             test_search(query, limit=3)
        
#         print(f"\n{'='*60}")
#         print(f"✓ HOÀN THÀNH TẤT CẢ CÁC BƯỚC!")
#         print(f"{'='*60}\n")
        
#     except Exception as e:
#         print(f"\n✗ LỖI: {e}")
#         raise


# if __name__ == "__main__":
#     main()