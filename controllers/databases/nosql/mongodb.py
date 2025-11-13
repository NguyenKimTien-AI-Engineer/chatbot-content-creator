"""
MongoDB connection và configuration cho AI Content Generator.
"""
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import json
from dotenv import load_dotenv

load_dotenv()


class MongoDBManager:
    """Quản lý kết nối MongoDB với async support."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.templates_collection: Optional[AsyncIOMotorCollection] = None
        self.content_history_collection: Optional[AsyncIOMotorCollection] = None
        self.products_collection: Optional[AsyncIOMotorCollection] = None
        self.post_types_collection: Optional[AsyncIOMotorCollection] = None
        
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
            database = os.getenv("MONGODB_DATABASE", "mekongai_social")
            
            if username and password:
                self.connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
            else:
                self.connection_string = f"mongodb://{host}:{port}/{database}"
        
        self.database_name = os.getenv("MONGODB_DATABASE", "mekongai_social")
        
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
            self.content_history_collection = self.database["content_history"]
            self.products_collection = self.database["products"]
            self.post_types_collection = self.database["post_types"]
            
            # Tạo index cho timestamp để query nhanh hơn
            try:
                await self.templates_collection.create_index([("timestamp", -1)])
                await self.content_history_collection.create_index([("created_at", -1)])
                await self.content_history_collection.create_index([("user_id", 1)])
                await self.products_collection.create_index([("sku", 1)])
                await self.products_collection.create_index([("name", "text")])
                await self.products_collection.create_index([("data.category", 1)])
                await self.post_types_collection.create_index([("key", 1)], unique=True)
                await self.post_types_collection.create_index([("full_name", 1)])
                print("[MONGODB] Indexes created successfully")
            except Exception as index_error:
                print(f"[MONGODB] Warning: Some indexes could not be created: {index_error}")
            
            print(f"[MONGODB] Successfully connected to database: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[MONGODB] Connection failure: {e}")
            return False
        except Exception as e:
            print(f"[MONGODB] Unexpected error during connection: {e}")
            print(f"[MONGODB] Connection string format may be invalid: {self.connection_string[:50]}...")
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

    async def save_content_history(self, content_data: Dict[str, Any]) -> Optional[str]:
        """
        Lưu lịch sử content vào database.
        
        Args:
            content_data: Dữ liệu content history
            
        Returns:
            str: ID của content history đã lưu
        """
        if self.content_history_collection is None:
            return None
            
        try:
            # Thêm timestamp
            now = datetime.utcnow()
            content_data.update({
                "created_at": now,
                "updated_at": now
            })
            
            result = await self.content_history_collection.insert_one(content_data)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Lỗi khi lưu content history: {e}")
            return None
    
    async def get_content_history_list(self, user_id: str = "default_user", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Lấy danh sách lịch sử content của user.
        
        Args:
            user_id: ID của user
            limit: Số lượng record tối đa
            
        Returns:
            List: Danh sách content history
        """
        if self.content_history_collection is None:
            return []
            
        try:
            cursor = self.content_history_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            histories = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                # Tạo preview từ post_content thay vì toàn bộ content
                content_str = doc.get("content", "")
                try:
                    content_obj = json.loads(content_str)
                    post_content = content_obj.get("post_content", "")
                    # Lấy 150 ký tự đầu của post_content
                    doc["preview"] = post_content[:150] + "..." if len(post_content) > 150 else post_content
                except (json.JSONDecodeError, TypeError) as e: # ignore: e
                    # Fallback nếu không parse được JSON
                    doc["preview"] = content_str[:100] + "..." if len(content_str) > 100 else content_str
                histories.append(doc)
                
            return histories
            
        except Exception as e:
            print(f"Lỗi khi lấy danh sách content history: {e}")
            return []
    
    async def get_content_history_by_id(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết content history theo ID.
        
        Args:
            history_id: ID của content history
            
        Returns:
            Dict: Chi tiết content history
        """
        if self.content_history_collection is None:
            return None
            
        try:
            from bson import ObjectId
            doc = await self.content_history_collection.find_one({"_id": ObjectId(history_id)})
            
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return doc
                
            return None
            
        except Exception as e:
            print(f"Lỗi khi lấy content history: {e}")
            return None
    
    async def delete_content_history(self, history_id: str) -> bool:
        """
        Xóa content history theo ID.
        
        Args:
            history_id: ID của content history
            
        Returns:
            bool: True nếu xóa thành công
        """
        if self.content_history_collection is None:
            return False
            
        try:
            from bson import ObjectId
            result = await self.content_history_collection.delete_one({"_id": ObjectId(history_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Lỗi khi xóa content history: {e}")
            return False

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


# Content History Methods - thêm vào class MongoDBManager
async def save_content_history(content_data: Dict[str, Any]) -> Optional[str]:
    """
    Utility function để lưu content history.
    
    Args:
        content_data: Dữ liệu content history
        
    Returns:
        str: ID của content history đã lưu
    """
    manager = await get_mongodb_manager()
    return await manager.save_content_history(content_data)


async def get_content_history_list(user_id: str = "default_user", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Utility function để lấy danh sách content history.
    
    Args:
        user_id: ID của user
        limit: Số lượng record tối đa
        
    Returns:
        List: Danh sách content history
    """
    manager = await get_mongodb_manager()
    return await manager.get_content_history_list(user_id, limit)


async def get_content_history_by_id(history_id: str) -> Optional[Dict[str, Any]]:
    """
    Utility function để lấy chi tiết content history.
    
    Args:
        history_id: ID của content history
        
    Returns:
        Dict: Chi tiết content history
    """
    manager = await get_mongodb_manager()
    return await manager.get_content_history_by_id(history_id)


async def delete_content_history(history_id: str) -> bool:
    """
    Utility function để xóa content history.
    
    Args:
        history_id: ID của content history
        
    Returns:
        bool: True nếu xóa thành công
    """
    manager = await get_mongodb_manager()
    return await manager.delete_content_history(history_id)


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