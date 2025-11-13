"""
Products API router cho Agent Content Generator.

Cung cấp CRUD operations cho products collection.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse

from api.schema_products import (
    ProductResponse,
    ProductListResponse,
    ProductSearchRequest,
    ProductCategoryResponse,
    ErrorResponse,
    ProductCreateRequest
)
from controllers.databases.nosql.mongodb import get_mongodb_manager, MongoDBManager

router = APIRouter()


@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="Lấy danh sách sản phẩm",
    description="Lấy danh sách sản phẩm với phân trang"
)
async def get_products(
    limit: int = Query(50, ge=1, le=100, description="Số lượng sản phẩm tối đa"),
    skip: int = Query(0, ge=0, description="Số lượng sản phẩm bỏ qua"),
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductListResponse:
    """
    Lấy danh sách sản phẩm với phân trang.
    
    Args:
        limit: Số lượng sản phẩm tối đa (1-100)
        skip: Số lượng sản phẩm bỏ qua
        db: MongoDB manager instance
        
    Returns:
        ProductListResponse: Danh sách sản phẩm
    """
    try:
        products = await db.get_products(limit=limit, skip=skip)
        
        return ProductListResponse(
            success=True,
            message="Lấy danh sách sản phẩm thành công",
            data=products,
            total=len(products)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy danh sách sản phẩm"
        )


@router.get(
    "/products/category/{category}",
    response_model=ProductListResponse,
    summary="Lấy sản phẩm theo category",
    description="Lấy danh sách sản phẩm theo loại (túi, giày, ví)"
)
async def get_products_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=100, description="Số lượng sản phẩm tối đa"),
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductListResponse:
    """
    Lấy danh sách sản phẩm theo category.
    
    Args:
        category: Loại sản phẩm (bag, shoes, wallet)
        limit: Số lượng sản phẩm tối đa
        db: MongoDB manager instance
        
    Returns:
        ProductListResponse: Danh sách sản phẩm theo category
    """
    try:
        # Validate category
        valid_categories = ["bag", "shoes", "wallet"]
        if category.lower() not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category không hợp lệ. Chỉ chấp nhận: {', '.join(valid_categories)}"
            )
        
        products = await db.get_products_by_category(category=category, limit=limit)
        
        return ProductListResponse(
            success=True,
            message=f"Lấy danh sách sản phẩm {category} thành công",
            data=products,
            total=len(products)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy sản phẩm theo category"
        )


@router.get(
    "/products/category/{category}/names",
    response_model=ProductCategoryResponse,
    summary="Lấy tên sản phẩm theo category",
    description="Lấy danh sách tên sản phẩm theo loại để hiển thị trong dropdown"
)
async def get_product_names_by_category(
    category: str,
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductCategoryResponse:
    """
    Lấy danh sách tên sản phẩm theo category.
    
    Args:
        category: Loại sản phẩm (bag, shoes, wallet)
        db: MongoDB manager instance
        
    Returns:
        ProductCategoryResponse: Danh sách tên sản phẩm
    """
    try:
        # Validate category
        valid_categories = ["bag", "shoes", "wallet"]
        if category.lower() not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category không hợp lệ. Chỉ chấp nhận: {', '.join(valid_categories)}"
            )
        
        product_names = await db.get_product_names_by_category(category=category)
        
        return ProductCategoryResponse(
            success=True,
            message=f"Lấy danh sách tên sản phẩm {category} thành công",
            category=category,
            product_names=product_names
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy tên sản phẩm theo category"
        )


@router.post(
    "/products/search",
    response_model=ProductListResponse,
    summary="Tìm kiếm sản phẩm",
    description="Tìm kiếm sản phẩm theo category và từ khóa"
)
async def search_products(
    search_request: ProductSearchRequest,
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductListResponse:
    """
    Tìm kiếm sản phẩm theo category và từ khóa.
    
    Args:
        search_request: Request body chứa thông tin tìm kiếm
        db: MongoDB manager instance
        
    Returns:
        ProductListResponse: Danh sách sản phẩm tìm được
    """
    try:
        # Validate category nếu có
        if search_request.category:
            valid_categories = ["bag", "shoes", "wallet"]
            if search_request.category.lower() not in valid_categories:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category không hợp lệ. Chỉ chấp nhận: {', '.join(valid_categories)}"
                )
        
        if search_request.category:
            # Tìm kiếm theo category và query
            products = await db.search_products_by_category_and_name(
                category=search_request.category,
                search_query=search_request.query or "",
                limit=search_request.limit
            )
        else:
            # Tìm kiếm general
            products = await db.search_products(
                query=search_request.query or "",
                limit=search_request.limit
            )
        
        return ProductListResponse(
            success=True,
            message="Tìm kiếm sản phẩm thành công",
            data=products,
            total=len(products)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi tìm kiếm sản phẩm"
        )


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Lấy chi tiết sản phẩm",
    description="Lấy thông tin chi tiết của một sản phẩm theo ID"
)
async def get_product_by_id(
    product_id: str,
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductResponse:
    """
    Lấy thông tin chi tiết sản phẩm theo ID.
    
    Args:
        product_id: ID của sản phẩm
        db: MongoDB manager instance
        
    Returns:
        ProductResponse: Thông tin chi tiết sản phẩm
    """
    try:
        # Thử tìm theo SKU trước
        product = await db.get_product_by_sku(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy sản phẩm"
            )
        
        return ProductResponse(
            success=True,
            message="Lấy thông tin sản phẩm thành công",
            data=product
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy thông tin sản phẩm"
        )


@router.post(
    "/products",
    response_model=ProductResponse,
    summary="Tạo sản phẩm mới",
    description="Tạo một sản phẩm mới trong hệ thống"
)
async def create_product(
    payload: ProductCreateRequest,
    db: MongoDBManager = Depends(get_mongodb_manager)
) -> ProductResponse:
    """
    Tạo mới sản phẩm dựa trên dữ liệu đầu vào.
    """
    try:
        created = await db.create_product(payload.dict())
        if not created:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể tạo sản phẩm")
        return ProductResponse(success=True, message="Tạo sản phẩm thành công", data=created)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi server khi tạo sản phẩm")