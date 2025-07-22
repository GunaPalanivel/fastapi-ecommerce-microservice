"""
Product service layer handling business logic and database operations.
"""

import logging
from typing import List, Optional
from datetime import datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from db import get_collection
from schemas.product import ProductIn, ProductOut
from utils.pagination import PaginationParams

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product operations."""
    
    def __init__(self):
        self.collection = get_collection("products")
    
    async def create_product(self, product: ProductIn) -> ProductOut:
        """
        Create a new product in the database.
        
        Args:
            product: Product data to create
            
        Returns:
            Created product with generated ID
            
        Raises:
            ValueError: If product data is invalid
        """
        try:
            # Prepare product document
            product_doc = {
                "name": product.name,
                "price": product.price,
                "size": product.size,
                "available_quantity": product.available_quantity,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into database
            result = await self.collection.insert_one(product_doc)
            
            if not result.inserted_id:
                raise ValueError("Failed to create product")
            
            # Retrieve and return the created product
            created_product = await self.collection.find_one({"_id": result.inserted_id})
            
            return ProductOut(
                _id=str(created_product["_id"]),
                name=created_product["name"],
                price=created_product["price"],
                size=created_product["size"],
                available_quantity=created_product["available_quantity"]
            )
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise
    
    async def list_products(
        self,
        name_filter: Optional[str] = None,
        size_filter: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> List[ProductOut]:
        """
        Retrieve products with optional filtering and pagination.
        
        Args:
            name_filter: Optional name filter with regex support
            size_filter: Optional size filter
            pagination: Pagination parameters
            
        Returns:
            List of products matching criteria
        """
        try:
            # Build query filters
            query = {}
            
            if name_filter:
                # Support partial/regex search for name
                query["name"] = {"$regex": name_filter, "$options": "i"}
            
            if size_filter:
                # Filter products that have the specified size
                query["size"] = {"$in": [size_filter.lower()]}
            
            # Create cursor with query
            cursor = self.collection.find(query)
            
            # Apply pagination
            if pagination:
                cursor = cursor.skip(pagination.offset).limit(pagination.limit)
            
            # Sort by _id for consistent pagination
            cursor = cursor.sort("_id", 1)
            
            # Fetch results
            products = await cursor.to_list(length=None)
            
            # Convert to response models
            return [
                ProductOut(
                    _id=str(product["_id"]),
                    name=product["name"],
                    price=product["price"],
                    size=product["size"],
                    available_quantity=product["available_quantity"]
                )
                for product in products
            ]
            
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise
    
    async def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """
        Retrieve a product by its ID.
        
        Args:
            product_id: Product ID to search for
            
        Returns:
            Product document if found, None otherwise
        """
        try:
            if not ObjectId.is_valid(product_id):
                return None
                
            return await self.collection.find_one({"_id": ObjectId(product_id)})
            
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            raise
    
    async def update_product_quantity(self, product_id: str, quantity_change: int) -> bool:
        """
        Update product available quantity (for order processing).
        
        Args:
            product_id: Product ID to update
            quantity_change: Change in quantity (negative for orders)
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {
                    "_id": ObjectId(product_id),
                    "available_quantity": {"$gte": abs(quantity_change) if quantity_change < 0 else 0}
                },
                {
                    "$inc": {"available_quantity": quantity_change},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating product quantity: {str(e)}")
            raise
