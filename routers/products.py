"""
Product router handling all product-related endpoints.
Implements create and list operations with comprehensive filtering and pagination.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from schemas.product import ProductIn, ProductOut
from services.product_service import ProductService
from utils.pagination import PaginationParams

logger = logging.getLogger(__name__)
router = APIRouter(tags=["products"])


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def create_product(product: ProductIn) -> ProductOut:
    """
    Create a new product in the system.
    
    Args:
        product: Product data including name, price, size options, and quantity
        
    Returns:
        Created product with generated ID
        
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    """
    try:
        logger.info(f"Creating new product: {product.name}")
        
        service = ProductService()
        created_product = await service.create_product(product)
        
        logger.info(f"Product created successfully with ID: {created_product.id}")
        return created_product
        
    except ValueError as e:
        logger.warning(f"Product creation validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Product creation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.get("/products", status_code=status.HTTP_200_OK, response_model=List[ProductOut])
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports partial search)"),
    size: Optional[str] = Query(None, description="Filter by size (e.g., 'large')"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
) -> List[ProductOut]:
    """
    Retrieve a list of products with optional filtering and pagination.
    
    Query Parameters:
        name: Optional name filter with regex support for partial matching
        size: Optional size filter to find products with specific size
        limit: Maximum number of products to return (1-100)
        offset: Number of products to skip for pagination
        
    Returns:
        List of products matching the criteria
        
    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        logger.info(f"Listing products with filters - name: {name}, size: {size}")
        
        service = ProductService()
        pagination = PaginationParams(limit=limit, offset=offset)
        
        products = await service.list_products(
            name_filter=name,
            size_filter=size,
            pagination=pagination
        )
        
        logger.info(f"Retrieved {len(products)} products")
        return products
        
    except Exception as e:
        logger.error(f"Product listing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )
