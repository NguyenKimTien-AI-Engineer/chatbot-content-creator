"""
MongoDB connection và configuration cho AI Content Generator.
"""
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import uuid
from dotenv import load_dotenv

load_dotenv()


class MongoDBManager:
    """Quản lý kết nối MongoDB với async support."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.templates_collection: Optional[AsyncIOMotorCollection] = None
        self.products_collection: Optional[AsyncIOMotorCollection] = None
        self.post_types_collection: Optional[AsyncIOMotorCollection] = None
        self.histories_collection: Optional[AsyncIOMotorCollection] = None
        self.sessions_collection: Optional[AsyncIOMotorCollection] = None
        self.images_collection: Optional[AsyncIOMotorCollection] = None
        
        # Cấu hình từ environment variables
        self.connection_string = os.getenv(
            "MONGODB_CONNECTION", 
            ""
        )
        
        # Nếu không có connection string, build từ các thành phần
        if not self.connection_string:
            host = os.getenv("MONGODB_HOST", "localhost")
            port = int(os.getenv("MONGODB_PORT", "27017"))
            username = os.getenv("MONGODB_USERNAME", "")
            password = os.getenv("MONGODB_PASSWORD", "")
            database = os.getenv("MONGODB_DATABASE", "")
            
            if username and password:
                self.connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
            else:
                self.connection_string = f"mongodb://{host}:{port}/{database}"
        
        self.database_name = os.getenv("MONGODB_DATABASE", "")
        
    async def connect(self) -> bool:
        """
        Kết nối đến MongoDB.
        
        Returns:
            bool: True nếu kết nối thành công, False nếu thất bại
        """
        try:
            # Validate connection string
            if not self.connection_string or self.connection_string.strip() == "":
                print("[MONGODB] Error: Connection string is empty")
                return False
                
            print(f"[MONGODB] Attempting to connect with: {self.connection_string[:50]}...")
            
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=10000,  # Tăng timeout lên 10 giây
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=10,
                minPoolSize=1
            )
            
            # Test connection with ping
            await self.client.admin.command('ping')
            print("[MONGODB] Connection test successful")
            
            self.database = self.client[self.database_name]
            self.templates_collection = self.database["templates"]
            self.products_collection = self.database["products"]
            self.post_types_collection = self.database["post_types"]
            self.histories_collection = self.database["histories"]
            self.sessions_collection = self.database["sessions"]
            self.images_collection = self.database["images"]
            
            # Tạo index cho timestamp để query nhanh hơn
            try:
                await self.templates_collection.create_index([("timestamp", -1)])
                await self.products_collection.create_index([("sku", 1)])
                await self.products_collection.create_index([("name", "text")])
                await self.products_collection.create_index([("data.category", 1)])
                await self.post_types_collection.create_index([("key", 1)], unique=True)
                await self.post_types_collection.create_index([("full_name", 1)])
                
                # Tạo indexes cho histories collection
                await self.histories_collection.create_index([("user_id", 1), ("session_id", 1)])
                await self.histories_collection.create_index([("history_id", 1)], unique=True)
                await self.histories_collection.create_index([("timestamp", -1)])
                await self.histories_collection.create_index([("user_id", 1), ("timestamp", -1)])
                
                # Tạo indexes cho sessions collection
                await self.sessions_collection.create_index([("session_id", 1)], unique=True)
                await self.sessions_collection.create_index([("user_id", 1)])
                await self.sessions_collection.create_index([("created_at", -1)])
                
                # Tạo indexes cho images collection
                await self.images_collection.create_index([("image_id", 1)], unique=True)
                await self.images_collection.create_index([("user_id", 1)])
                await self.images_collection.create_index([("upload_date", -1)])
                
                print("[MONGODB] Indexes created successfully")
            except Exception as index_error:
                print(f"[MONGODB] Warning: Some indexes could not be created: {index_error}")
            
            print(f"[MONGODB] Successfully connected to database: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[MONGODB] Connection failure: {e}")
            return False

    async def cleanup_old_templates(self, keep_count: int = 10) -> int:
        """
        Xóa các template cũ, chỉ giữ lại số lượng template mới nhất.
        
        Args:
            keep_count: Số lượng template mới nhất cần giữ lại
            
        Returns:
            Số lượng template đã xóa
        """
        try:
            if self.database is None:
                await self.connect()
            
            if self.templates_collection is None:
                return 0
                
            collection = self.templates_collection
            
            # Đếm tổng số template
            total_count = await collection.count_documents({})
            
            if total_count <= keep_count:
                return 0
            
            # Lấy danh sách template cũ (sắp xếp theo created_at tăng dần)
            old_templates = await collection.find(
                {},
                {"_id": 1}
            ).sort("created_at", 1).limit(total_count - keep_count).to_list(None)
            
            if not old_templates:
                return 0
            
            # Xóa các template cũ
            old_ids = [template["_id"] for template in old_templates]
            result = await collection.delete_many({"_id": {"$in": old_ids}})
            
            return result.deleted_count
            
        except Exception as e:
            print(f"Lỗi khi cleanup templates: {e}")
            return 0
    
    async def disconnect(self):
        """Đóng kết nối MongoDB."""
        if self.client:
            self.client.close()
            
    async def save_template(self, user_configuration: Dict[str, Any]) -> Optional[str]:
        """
        Lưu template configuration vào MongoDB.
        
        Args:
            user_configuration: Dictionary chứa cấu hình người dùng
            
        Returns:
            str: ID của document đã lưu, None nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.templates_collection is None:
                return None
                
            # Thêm timestamp nếu chưa có
            if "timestamp" not in user_configuration:
                user_configuration["timestamp"] = datetime.now().isoformat()
            
            # Thêm metadata
            template_doc = {
                **user_configuration,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "version": "1.0"
            }
            
            result = await self.templates_collection.insert_one(template_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Lỗi khi lưu template: {e}")
            return None
    
    async def get_latest_template(self) -> Optional[Dict[str, Any]]:
        """
        Lấy template mới nhất từ MongoDB.
        
        Returns:
            Dict: Template configuration, None nếu không tìm thấy
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.templates_collection is None:
                return None
                
            # Tìm document mới nhất theo timestamp
            cursor = self.templates_collection.find().sort("created_at", -1).limit(1)
            
            async for document in cursor:
                # Loại bỏ các field MongoDB internal
                document.pop("_id", None)
                document.pop("created_at", None)
                document.pop("updated_at", None)
                document.pop("version", None)
                return document
                
            return None
            
        except Exception as e:
            print(f"Lỗi khi lấy template: {e}")
            return None
    
    async def get_all_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lấy danh sách templates với giới hạn số lượng.
        
        Args:
            limit: Số lượng templates tối đa
            
        Returns:
            List[Dict]: Danh sách templates
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.templates_collection is None:
                return []
                
            templates = []
            cursor = self.templates_collection.find().sort("created_at", -1).limit(limit)
            
            async for document in cursor:
                document.pop("_id", None)
                templates.append(document)
                
            return templates
            
        except Exception as e:
            print(f"Lỗi khi lấy danh sách templates: {e}")
            return []
    
    async def delete_old_templates(self, keep_count: int = 50):
        """
        Xóa các templates cũ, chỉ giữ lại số lượng nhất định.
        
        Args:
            keep_count: Số lượng templates muốn giữ lại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.templates_collection is None:
                return
                
            # Đếm tổng số documents
            total_count = await self.templates_collection.count_documents({})
            
            if total_count <= keep_count:
                return
            
            # Lấy danh sách IDs của các documents cần xóa
            skip_count = keep_count
            cursor = self.templates_collection.find({}, {"_id": 1}).sort("created_at", -1).skip(skip_count)
            
            ids_to_delete = []
            async for doc in cursor:
                ids_to_delete.append(doc["_id"])
            
            if ids_to_delete:
                await self.templates_collection.delete_many({"_id": {"$in": ids_to_delete}})
                print(f"Đã xóa {len(ids_to_delete)} templates cũ")
                
        except Exception as e:
            print(f"Lỗi khi xóa templates cũ: {e}")

    async def save_products(self, products_data: List[Dict[str, Any]]) -> int:
        """
        Lưu danh sách sản phẩm vào MongoDB.
        
        Args:
            products_data: Danh sách sản phẩm
            
        Returns:
            int: Số lượng sản phẩm đã lưu thành công
        """
        if self.products_collection is None:
            return 0
            
        if not products_data:
            return 0
            
        try:
            # Xử lý từng sản phẩm để chuẩn hóa dữ liệu
            processed_products = []
            for product in products_data:
                # Tạo bản sao để không thay đổi dữ liệu gốc
                processed_product = product.copy()
                
                # Xử lý _id nếu có
                if '_id' in processed_product and isinstance(processed_product['_id'], dict):
                    if '$oid' in processed_product['_id']:
                        processed_product['original_id'] = processed_product['_id']['$oid']
                        del processed_product['_id']
                
                # Xử lý create_at và update_at
                if 'create_at' in processed_product and isinstance(processed_product['create_at'], dict):
                    if '$date' in processed_product['create_at']:
                        processed_product['create_at'] = processed_product['create_at']['$date']
                
                if 'update_at' in processed_product and isinstance(processed_product['update_at'], dict):
                    if '$date' in processed_product['update_at']:
                        processed_product['update_at'] = processed_product['update_at']['$date']
                
                # Thêm timestamp nếu chưa có
                now = datetime.utcnow()
                if "create_at" not in processed_product:
                    processed_product["create_at"] = now
                if "update_at" not in processed_product:
                    processed_product["update_at"] = now
                if 'created_at' not in processed_product:
                    processed_product['created_at'] = now
                if 'updated_at' not in processed_product:
                    processed_product['updated_at'] = now
                
                processed_products.append(processed_product)
            
            # Sử dụng upsert để tránh duplicate
            from pymongo import UpdateOne
            operations = []
            for product in processed_products:
                filter_query = {'sku': product['sku']} if 'sku' in product else {'name': product.get('name')}
                operations.append(
                    UpdateOne(
                        filter_query,
                        {'$set': product},
                        upsert=True
                    )
                )
            
            # Thực hiện bulk write
            if operations:
                result = await self.products_collection.bulk_write(operations)
                return result.upserted_count + result.modified_count
            
            return 0
            
        except Exception as e:
            print(f"Lỗi khi lưu products: {e}")
            return 0
    
    async def get_products(self, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lấy danh sách sản phẩm với phân trang.
        
        Args:
            limit: Số lượng sản phẩm tối đa
            skip: Số lượng sản phẩm bỏ qua
            
        Returns:
            List: Danh sách sản phẩm
        """
        if self.products_collection is None:
            return []
            
        try:
            cursor = self.products_collection.find().skip(skip).limit(limit)
            products = []
            
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                products.append(doc)
                
            return products
            
        except Exception as e:
            print(f"Lỗi khi lấy danh sách products: {e}")
            return []
    
    async def search_products(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Tìm kiếm sản phẩm theo tên hoặc mô tả.
        
        Args:
            query: Từ khóa tìm kiếm
            limit: Số lượng kết quả tối đa
            
        Returns:
            List: Danh sách sản phẩm tìm được
        """
        if self.products_collection is None:
            return []
            
        try:
            cursor = self.products_collection.find({
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"data.description": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit)
            
            products = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                products.append(doc)
                
            return products
            
        except Exception as e:
            print(f"Lỗi khi tìm kiếm products: {e}")
            return []
    
    async def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Lấy sản phẩm theo SKU.
        
        Args:
            sku: Mã SKU của sản phẩm
            
        Returns:
            Dict: Thông tin sản phẩm
        """
        if self.products_collection is None:
            return None
            
        try:
            doc = await self.products_collection.find_one({"sku": sku})
            
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return doc
                
            return None
            
        except Exception as e:
            print(f"Lỗi khi lấy product theo SKU: {e}")
            return None

    async def get_products_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lấy danh sách sản phẩm theo category (túi, giày, ví).
        
        Args:
            category: Loại sản phẩm (bag/túi, shoes/giày, wallet/ví)
            limit: Số lượng sản phẩm tối đa
            
        Returns:
            List: Danh sách sản phẩm theo category
        """
        if self.products_collection is None:
            return []
            
        try:
            # Mapping category names
            category_mapping = {
                "bag": ["túi", "bag"],
                "shoes": ["giày", "shoes"],
                "wallet": ["ví", "wallet"]
            }
            
            search_terms = category_mapping.get(category.lower(), [category])
            
            # Tạo regex pattern cho tìm kiếm
            regex_patterns = []
            for term in search_terms:
                regex_patterns.append({"name": {"$regex": term, "$options": "i"}})
            
            query = {"$or": regex_patterns}
            
            cursor = self.products_collection.find(query).limit(limit)
            products = []
            
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                products.append(doc)
                
            return products
            
        except Exception as e:
            print(f"Lỗi khi lấy products theo category: {e}")
            return []

    async def get_product_names_by_category(self, category: str) -> List[str]:
        """
        Lấy danh sách tên sản phẩm theo category để hiển thị trong dropdown.
        
        Args:
            category: Loại sản phẩm (bag/túi, shoes/giày, wallet/ví)
            
        Returns:
            List: Danh sách tên sản phẩm đầy đủ
        """
        if self.products_collection is None:
            return []
            
        try:
            # Mapping category names
            category_mapping = {
                "bag": ["túi", "bag"],
                "shoes": ["giày", "shoes"], 
                "wallet": ["ví", "wallet"]
            }
            
            search_terms = category_mapping.get(category.lower(), [category])
            
            # Tạo regex pattern cho tìm kiếm
            regex_patterns = []
            for term in search_terms:
                regex_patterns.append({"name": {"$regex": term, "$options": "i"}})
            
            query = {"$or": regex_patterns}
            
            cursor = self.products_collection.find(query, {"name": 1})
            product_names = []
            
            async for doc in cursor:
                # Lấy tên sản phẩm đầy đủ
                name = doc.get("name", "")
                if name.strip():
                    product_names.append(name.strip())
                
            # Loại bỏ duplicate và sort
            unique_names = list(set(product_names))
            unique_names.sort()
            
            return unique_names
            
        except Exception as e:
            print(f"Lỗi khi lấy product names theo category: {e}")
            return []

    async def search_products_by_category_and_name(self, category: str, search_query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Tìm kiếm sản phẩm theo category và tên sản phẩm.
        
        Args:
            category: Loại sản phẩm (bag/túi, shoes/giày, wallet/ví)
            search_query: Từ khóa tìm kiếm trong tên sản phẩm
            limit: Số lượng kết quả tối đa
            
        Returns:
            List: Danh sách sản phẩm tìm được
        """
        if self.products_collection is None:
            return []
        
        try:
            # Mapping category names
            category_mapping = {
                "bag": ["túi", "bag"],
                "shoes": ["giày", "shoes"],
                "wallet": ["ví", "wallet"]
            }
            
            search_terms = category_mapping.get(category.lower(), [category])
            
            # Tạo query cho category
            category_patterns = []
            for term in search_terms:
                category_patterns.append({"name": {"$regex": term, "$options": "i"}})
            
            query = {"$and": [{"$or": category_patterns}]}
            
            # Thêm search query nếu có
            if search_query.strip():
                query["$and"].append({
                    "$or": [
                        {"name": {"$regex": search_query, "$options": "i"}},
                        {"data.description": {"$regex": search_query, "$options": "i"}}
                    ]
                })
            
            cursor = self.products_collection.find(query).limit(limit)
            products = []
            
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                products.append(doc)
                
            return products
            
        except Exception as e:
            print(f"Lỗi khi tìm kiếm products: {e}")
            return []
    
    async def create_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tạo sản phẩm mới.

        Args:
            product: Dữ liệu sản phẩm đầu vào gồm name, pricing, media, data

        Returns:
            Dict hoặc None: Document sản phẩm đã tạo (đã loại bỏ _id) hoặc None nếu lỗi
        """
        if self.products_collection is None:
            return None

        try:
            now = datetime.utcnow()

            # Chuẩn hóa dữ liệu cơ bản
            name = (product.get("name") or "").strip()
            if not name:
                raise ValueError("Tên sản phẩm không được để trống")

            # Tự tạo SKU nếu thiếu
            sku = (product.get("sku") or "").strip()
            if not sku:
                base = name.lower().replace(" ", "-")
                sku = f"{base}-{int(now.timestamp())}"

            # Build document
            doc: Dict[str, Any] = {
                "sku": sku,
                "name": name,
                "pricing": product.get("pricing") or {},
                "media": product.get("media") or [],
                "data": product.get("data") or {},
                "created_at": now,
                "updated_at": now,
            }

            result = await self.products_collection.insert_one(doc)

            created = await self.products_collection.find_one({"_id": result.inserted_id})
            if not created:
                return None

            created["id"] = str(created["_id"])
            created.pop("_id", None)
            return created
        except Exception as e:
            print(f"Lỗi khi tạo sản phẩm: {e}")
            return None

    async def list_post_types(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Lấy danh sách loại bài viết.

        Args:
            active_only: Chỉ lấy post types đang active

        Returns:
            List[Dict]: Danh sách post types đã chuẩn hóa (không có _id)
        """
        if self.post_types_collection is None:
            return []

        try:
            query: Dict[str, Any] = {}
            if active_only:
                query["active"] = True

            cursor = self.post_types_collection.find(query).sort("created_at", -1)
            results: List[Dict[str, Any]] = []
            async for doc in cursor:
                doc.pop("_id", None)
                results.append(doc)
            return results
        except Exception as e:
            print(f"Lỗi khi lấy danh sách post types: {e}")
            return []

    async def create_post_type(self, key: str, full_name: str, description: Optional[str] = None) -> bool:
        """Tạo loại bài viết mới hoặc cập nhật nếu key đã tồn tại.

        Args:
            key: Khóa nội bộ (ví dụ: product_showcases)
            full_name: Tên hiển thị đầy đủ (ví dụ: "Giới thiệu sản phẩm mới (Product Showcases)")
            description: Mô tả tuỳ chọn

        Returns:
            bool: True nếu tạo/cập nhật thành công
        """
        if self.post_types_collection is None:
            return False

        try:
            now = datetime.utcnow()
            key_norm = key.strip()
            full_norm = full_name.strip()
            if not key_norm or not full_norm:
                raise ValueError("Key và Full Name của post type không được để trống")

            # Upsert theo key
            await self.post_types_collection.update_one(
                {"key": key_norm},
                {
                    "$set": {
                        "key": key_norm,
                        "full_name": full_norm,
                        "description": description,
                        "updated_at": now,
                        "active": True,
                    },
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"Lỗi khi tạo/cập nhật post type: {e}")
            return False

    async def delete_post_type(self, key: str) -> bool:
        """Xóa (deactivate) post type theo key.

        Args:
            key: Khóa post type

        Returns:
            bool: True nếu cập nhật thành công
        """
        if self.post_types_collection is None:
            return False

        try:
            result = await self.post_types_collection.update_one(
                {"key": key.strip()}, {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Lỗi khi xóa post type: {e}")
            return False

    async def save_history(self, user_id: str, history_id: str, session_id: str, query: str, 
                          answer: str, feedback: str, feedback_status: str, 
                          references: Any, chart: Any, image_url: Optional[str] = None) -> Optional[str]:
        """
        Lưu lịch sử chat vào MongoDB.
        
        Args:
            user_id: ID của người dùng
            history_id: ID của lịch sử
            session_id: ID của session
            query: Câu hỏi của user
            answer: Câu trả lời của AI
            feedback: Phản hồi của user
            feedback_status: Trạng thái feedback
            references: Tài liệu tham khảo
            chart: Dữ liệu biểu đồ
            
        Returns:
            str: ID của document đã lưu, None nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return None
                
            # Tạo document lịch sử
            history_doc = {
                "history_id": history_id,
                "user_id": user_id,
                "session_id": session_id,
                "query": query,
                "answer": answer,
                "feedback": feedback,
                "feedback_status": feedback_status,
                "reference": references,
                "chart": chart,
                "image_url": image_url,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Lưu vào histories collection
            result = await self.histories_collection.insert_one(history_doc)
            
            # Cập nhật sessions collection
            if self.sessions_collection is not None:
                session_doc = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "last_activity": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Upsert session document
                await self.sessions_collection.update_one(
                    {"session_id": session_id, "user_id": user_id},
                    {"$set": session_doc},
                    upsert=True
                )
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Lỗi khi lưu history: {e}")
            return None
    
    async def get_history(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử chat theo user_id và session_id.
        
        Args:
            user_id: ID của người dùng
            session_id: ID của session
            
        Returns:
            List: Danh sách lịch sử chat
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return []
                
            cursor = self.histories_collection.find({
                "user_id": user_id,
                "session_id": session_id
            }).sort("timestamp", 1)  # Sắp xếp theo thời gian tăng dần
            
            history = []
            async for doc in cursor:
                # Loại bỏ _id MongoDB internal
                doc.pop("_id", None)
                history.append(doc)
                
            return history
            
        except Exception as e:
            print(f"Lỗi khi lấy history: {e}")
            return []
    
    async def get_all_history_user(self, user_id: str) -> List[List[Dict[str, Any]]]:
        """
        Lấy tất cả lịch sử của một user, nhóm theo session.
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            List: Danh sách các session history
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return []
                
            # Lấy danh sách các session_id unique của user
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$session_id"}},
                {"$sort": {"_id": -1}}
            ]
            
            sessions = []
            async for doc in self.histories_collection.aggregate(pipeline):
                session_id = doc["_id"]
                session_history = await self.get_history(user_id, session_id)
                if session_history:
                    sessions.append(session_history)
                    
            return sessions
            
        except Exception as e:
            print(f"Lỗi khi lấy tất cả history user: {e}")
            return []
    
    async def update_feedback(self, user_id: str, history_id: str, 
                               new_feedback: str, new_feedback_status: str, 
                               session_id: str = None) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Cập nhật feedback cho một lịch sử cụ thể.
        
        Args:
            user_id: ID của người dùng
            history_id: ID của lịch sử cần cập nhật
            new_feedback: Feedback mới
            new_feedback_status: Trạng thái feedback mới
            session_id: ID của session (optional)
            
        Returns:
            tuple: (success: bool, updated_entries: List)
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return False, []
                
            # Build query
            query = {
                "user_id": user_id,
                "history_id": history_id
            }
            
            if session_id:
                query["session_id"] = session_id
            
            # Build update document
            update_doc = {}
            if new_feedback is not None:
                update_doc["feedback"] = new_feedback
            if new_feedback_status is not None:
                update_doc["feedback_status"] = new_feedback_status
            
            if not update_doc:
                return False, []
                
            update_doc["updated_at"] = datetime.utcnow()
            
            # Cập nhật document
            result = await self.histories_collection.update_one(
                query,
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                # Lấy document đã cập nhật
                updated_doc = await self.histories_collection.find_one(query)
                if updated_doc:
                    updated_doc.pop("_id", None)
                    return True, [updated_doc]
                    
            return False, []
            
        except Exception as e:
            print(f"Lỗi khi cập nhật feedback: {e}")
            return False, []
    
    async def get_history_context(self, user_id: str, query: str, session_id: str, limit: int = 15) -> str:
        """
        Lấy context từ lịch sử chat để phục vụ cho query hiện tại.
        
        Args:
            user_id: ID của người dùng
            query: Câu hỏi hiện tại
            session_id: ID của session
            limit: Số lượng lịch sử tối đa
            
        Returns:
            str: Context string để gửi vào prompt
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return ""
                
            # Lấy lịch sử của session
            history = await self.get_history(user_id, session_id)
            
            # Giới hạn số lượng history
            if len(history) > limit:
                history = history[-limit:]
            
            # Build context string
            history_context = ""
            
            # Xóa answer của các entry cũ (trừ 3 entry cuối)
            for entry in history[:-3]:
                entry["answer"] = ""
            
            # Build context từ history
            for item in history:
                if item.get('query'):
                    history_context += f"- User: [{item['query']}]"
                if item.get('answer'):
                    history_context += f"\n- You: [{item['answer']}]"
            
            history_context += f"\n\n- User: {query}\n"
            
            return history_context
            
        except Exception as e:
            print(f"Lỗi khi lấy history context: {e}")
            return ""
    
    async def cleanup_old_history(self, keep_days: int = 30) -> int:
        """
        Xóa lịch sử cũ hơn số ngày chỉ định.
        
        Args:
            keep_days: Số ngày giữ lại lịch sử
            
        Returns:
            int: Số lượng documents đã xóa
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return 0
                
            # Tính thời gian cắt
            cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
            
            # Xóa các documents cũ hơn cutoff_date
            result = await self.histories_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                print(f"Đã xóa {deleted_count} history documents cũ hơn {keep_days} ngày")
                
            return deleted_count
            
        except Exception as e:
            print(f"Lỗi khi cleanup old history: {e}")
            return 0

    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Lấy tất cả sessions của một user.
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            List: Danh sách sessions
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.sessions_collection is None:
                return []
                
            sessions = await self.sessions_collection.find(
                {"user_id": user_id}
            ).sort("last_activity", -1).to_list(None)
            
            # Remove _id field
            for session in sessions:
                session.pop("_id", None)
                
            return sessions
            
        except Exception as e:
            print(f"Lỗi khi lấy user sessions: {e}")
            return []
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết của một session.
        
        Args:
            session_id: ID của session
            
        Returns:
            Dict: Thông tin session hoặc None
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.sessions_collection is None:
                return None
                
            session = await self.sessions_collection.find_one(
                {"session_id": session_id}
            )
            
            if session:
                session.pop("_id", None)
                
            return session
            
        except Exception as e:
            print(f"Lỗi khi lấy session info: {e}")
            return None
    
    async def delete_session(self, user_id: str, session_id: str) -> bool:
        """
        Xóa một session và toàn bộ history của nó.
        
        Args:
            user_id: ID của người dùng
            session_id: ID của session cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.sessions_collection is None or self.histories_collection is None:
                print(f"Collections not initialized: sessions={self.sessions_collection}, histories={self.histories_collection}")
                return False
            
            print(f"Attempting to delete session {session_id} for user {user_id}")
            
            # Xóa session
            session_result = await self.sessions_collection.delete_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            print(f"Session delete result: deleted_count={session_result.deleted_count}")
            
            # Xóa toàn bộ history của session
            history_result = await self.histories_collection.delete_many({
                "user_id": user_id,
                "session_id": session_id
            })
            
            print(f"History delete result: deleted_count={history_result.deleted_count}")
            
            success = session_result.deleted_count > 0 or history_result.deleted_count > 0
            print(f"Delete operation success: {success}")
            return success
            
        except Exception as e:
            print(f"Lỗi khi xóa session: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_user_history(self, user_id: str, session_id: Optional[str] = None, 
                              limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử của user với các bộ lọc và phân trang.
        
        Args:
            user_id: ID của người dùng
            session_id: ID của session (optional)
            limit: Số lượng bản ghi tối đa
            skip: Số lượng bản ghi bỏ qua
            
        Returns:
            List: Danh sách lịch sử
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return []
            
            # Build query
            query = {"user_id": user_id}
            if session_id:
                query["session_id"] = session_id
                
            # Get total count
            total_count = await self.histories_collection.count_documents(query)
            
            # Get paginated results
            cursor = self.histories_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            
            history = []
            async for doc in cursor:
                doc.pop("_id", None)
                history.append(doc)
                
            return history
            
        except Exception as e:
            print(f"Lỗi khi lấy user history: {e}")
            return []
    
    async def get_history_by_id(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy lịch sử theo ID.
        
        Args:
            history_id: ID của history
            
        Returns:
            Dict: Thông tin history hoặc None
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return None
                
            history = await self.histories_collection.find_one({"history_id": history_id})
            
            if history:
                history.pop("_id", None)
                
            return history
            
        except Exception as e:
            print(f"Lỗi khi lấy history by ID: {e}")
            return None
    
    async def delete_history(self, history_id: str) -> bool:
        """
        Xóa lịch sử theo ID.
        
        Args:
            history_id: ID của history cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.histories_collection is None:
                return False
                
            result = await self.histories_collection.delete_one({"history_id": history_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Lỗi khi xóa history: {e}")
            return False
    
    async def save_image(self, image_id: str, user_id: str, image_data: bytes, 
                        content_type: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Lưu ảnh vào MongoDB.
        
        Args:
            image_id: UUID của ảnh
            user_id: ID của người dùng
            image_data: Dữ liệu binary của ảnh
            content_type: Loại nội dung (image/jpeg, image/png, etc.)
            metadata: Metadata bổ sung (optional)
            
        Returns:
            str: ID của document đã lưu, None nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.images_collection is None:
                return None
                
            # Tạo document ảnh
            image_doc = {
                "image_id": image_id,
                "user_id": user_id,
                "binary_data": image_data,
                "content_type": content_type,
                "upload_date": datetime.utcnow(),
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }
            
            result = await self.images_collection.insert_one(image_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Lỗi khi lưu ảnh: {e}")
            return None
    
    async def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy ảnh từ MongoDB theo image_id.
        
        Args:
            image_id: UUID của ảnh
            
        Returns:
            Dict: Document ảnh hoặc None nếu không tìm thấy
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.images_collection is None:
                return None
                
            image = await self.images_collection.find_one({"image_id": image_id})
            
            if image:
                image.pop("_id", None)
                
            return image
            
        except Exception as e:
            print(f"Lỗi khi lấy ảnh: {e}")
            return None
    
    async def delete_image(self, image_id: str, user_id: str) -> bool:
        """
        Xóa ảnh khỏi MongoDB.
        
        Args:
            image_id: UUID của ảnh
            user_id: ID của người dùng (để xác thực)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.images_collection is None:
                return False
                
            result = await self.images_collection.delete_one({
                "image_id": image_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Lỗi khi xóa ảnh: {e}")
            return False
    
    async def get_user_images(self, user_id: str, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lấy danh sách ảnh của user (không bao gồm binary_data để tối ưu).
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng ảnh tối đa
            skip: Số lượng ảnh bỏ qua
            
        Returns:
            List: Danh sách thông tin ảnh (không có binary_data)
        """
        try:
            if self.database is None:
                await self.connect()
                
            if self.images_collection is None:
                return []
                
            images = await self.images_collection.find(
                {"user_id": user_id},
                {"binary_data": 0}  # Loại trừ binary_data để tối ưu
            ).sort("upload_date", -1).skip(skip).limit(limit).to_list(None)
            
            # Remove _id field
            for image in images:
                image.pop("_id", None)
                
            return images
            
        except Exception as e:
            print(f"Lỗi khi lấy danh sách ảnh: {e}")
            return []

    
# Singleton instance
mongodb_manager = MongoDBManager()


async def get_mongodb_manager() -> MongoDBManager:
    """
    Dependency injection cho FastAPI.
    
    Returns:
        MongoDBManager: Instance đã kết nối
    """
    if not mongodb_manager.client:
        await mongodb_manager.connect()
    return mongodb_manager


# Utility functions
async def save_user_template(user_configuration: Dict[str, Any]) -> Optional[str]:
    """
    Utility function để lưu template.
    
    Args:
        user_configuration: Cấu hình người dùng
        
    Returns:
        str: ID của template đã lưu
    """
    manager = await get_mongodb_manager()
    return await manager.save_template(user_configuration)


async def load_latest_template() -> Optional[Dict[str, Any]]:
    """
    Utility function để lấy template mới nhất.
    
    Returns:
        Dict: Template configuration
    """
    manager = await get_mongodb_manager()
    return await manager.get_latest_template()


# Products utility functions
async def save_products(products_data: List[Dict[str, Any]]) -> int:
    """
    Utility function để lưu danh sách sản phẩm.
    
    Args:
        products_data: Danh sách sản phẩm
        
    Returns:
        int: Số lượng sản phẩm đã lưu
    """
    manager = await get_mongodb_manager()
    return await manager.save_products(products_data)


async def get_products(limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Utility function để lấy danh sách sản phẩm.
    
    Args:
        limit: Số lượng sản phẩm tối đa
        skip: Số lượng sản phẩm bỏ qua
        
    Returns:
        List: Danh sách sản phẩm
    """
    manager = await get_mongodb_manager()
    return await manager.get_products(limit, skip)


async def search_products(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Utility function để tìm kiếm sản phẩm.
    
    Args:
        query: Từ khóa tìm kiếm
        limit: Số lượng kết quả tối đa
        
    Returns:
        List: Danh sách sản phẩm tìm được
    """
    manager = await get_mongodb_manager()
    return await manager.search_products(query, limit)


async def get_product_by_sku(sku: str) -> Optional[Dict[str, Any]]:
    """
    Utility function để lấy sản phẩm theo SKU.
    
    Args:
        sku: Mã SKU của sản phẩm
        
    Returns:
        Dict: Thông tin sản phẩm
    """
    manager = await get_mongodb_manager()
    return await manager.get_product_by_sku(sku)

async def create_product(product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Utility function để tạo sản phẩm mới.

    Args:
        product_data: Dữ liệu sản phẩm bao gồm name, pricing, media, data

    Returns:
        Dict hoặc None: Document sản phẩm đã tạo
    """
    manager = await get_mongodb_manager()
    return await manager.create_product(product_data)


# Post Types utility functions
async def get_post_types(active_only: bool = True) -> List[Dict[str, Any]]:
    """Utility function để lấy danh sách loại bài viết.

    Args:
        active_only: Chỉ lấy các loại đang active

    Returns:
        List[Dict]: Danh sách post types
    """
    manager = await get_mongodb_manager()
    return await manager.list_post_types(active_only)


async def create_post_type(post_type: Dict[str, Any]) -> bool:
    """Utility function để tạo/cập nhật post type.

    Args:
        post_type: Dict chứa key, full_name, description

    Returns:
        bool: True nếu thành công
    """
    manager = await get_mongodb_manager()
    return await manager.create_post_type(
        key=post_type.get("key", ""),
        full_name=post_type.get("full_name", ""),
        description=post_type.get("description")
    )
