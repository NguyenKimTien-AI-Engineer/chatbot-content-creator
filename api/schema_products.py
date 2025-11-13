"""
Pydantic schemas cho Products API.

Định nghĩa các model để validate request/response data.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProductMedia(BaseModel):
    """Schema cho media của sản phẩm."""
    type: str = Field(..., description="Loại media (image, video)")
    url: str = Field(..., description="URL của media")
    alt_text: Optional[str] = Field(None, description="Alt text cho media")


class ProductPricing(BaseModel):
    """Schema cho thông tin giá của sản phẩm."""
    price: float = Field(..., description="Giá bán")
    currency: str = Field(default="VND", description="Đơn vị tiền tệ")
    cost: Optional[float] = Field(None, description="Giá gốc")


class ProductData(BaseModel):
    """Schema cho dữ liệu chi tiết sản phẩm."""
    description: str = Field(..., description="Mô tả sản phẩm")
    category: List[str] = Field(default=[], description="Danh mục sản phẩm")
    quantity: int = Field(default=0, description="Số lượng tồn kho")


class Product(BaseModel):
    """Schema cho sản phẩm."""
    id: Optional[str] = Field(None, description="ID của sản phẩm")
    name: str = Field(..., description="Tên sản phẩm")
    sku: str = Field(..., description="Mã SKU")
    pricing: ProductPricing = Field(..., description="Thông tin giá")
    media: List[ProductMedia] = Field(default=[], description="Danh sách media")
    data: ProductData = Field(..., description="Dữ liệu chi tiết")
    user_id: Optional[str] = Field(None, description="ID người dùng")
    company_id: Optional[str] = Field(None, description="ID công ty")
    created_at: Optional[datetime] = Field(None, description="Thời gian tạo")
    updated_at: Optional[datetime] = Field(None, description="Thời gian cập nhật")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProductCreateRequest(BaseModel):
    """Schema cho request tạo sản phẩm mới.

    Cho phép thiếu SKU, hệ thống sẽ tự sinh nếu không có.
    """
    name: str = Field(..., description="Tên sản phẩm")
    sku: Optional[str] = Field(None, description="Mã SKU (tùy chọn)")
    pricing: ProductPricing = Field(..., description="Thông tin giá")
    media: List[ProductMedia] = Field(default=[], description="Danh sách media")
    data: ProductData = Field(..., description="Dữ liệu chi tiết")


class ProductSearchRequest(BaseModel):
    """Schema cho request tìm kiếm sản phẩm."""
    query: Optional[str] = Field(None, description="Từ khóa tìm kiếm")
    category: Optional[str] = Field(None, description="Loại sản phẩm (bag, shoes, wallet)")
    limit: int = Field(default=20, ge=1, le=100, description="Số lượng kết quả tối đa")


class ProductResponse(BaseModel):
    """Schema cho response trả về một sản phẩm."""
    success: bool = Field(..., description="Trạng thái thành công")
    message: str = Field(..., description="Thông báo")
    data: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu sản phẩm")


class ProductListResponse(BaseModel):
    """Schema cho response trả về danh sách sản phẩm."""
    success: bool = Field(..., description="Trạng thái thành công")
    message: str = Field(..., description="Thông báo")
    data: List[Dict[str, Any]] = Field(default=[], description="Danh sách sản phẩm")
    total: int = Field(..., description="Tổng số sản phẩm")


class ProductCategoryResponse(BaseModel):
    """Schema cho response trả về tên sản phẩm theo category."""
    success: bool = Field(..., description="Trạng thái thành công")
    message: str = Field(..., description="Thông báo")
    category: str = Field(..., description="Loại sản phẩm")
    product_names: List[str] = Field(default=[], description="Danh sách tên sản phẩm")


class ErrorResponse(BaseModel):
    """Schema cho error response."""
    success: bool = Field(default=False, description="Trạng thái thành công")
    message: str = Field(..., description="Thông báo lỗi")
    error_code: Optional[str] = Field(None, description="Mã lỗi")
    details: Optional[Dict[str, Any]] = Field(None, description="Chi tiết lỗi")