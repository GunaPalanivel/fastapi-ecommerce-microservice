"""
Pydantic schemas for order data validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class OrderIn(BaseModel):
    """Schema for order creation requests."""
    
    user_id: str = Field(..., min_length=1, description="User ID placing the order")
    product_id: str = Field(..., min_length=1, description="Product ID being ordered")
    quantity: int = Field(..., gt=0, description="Quantity ordered (must be positive)")
    
    @validator('user_id', 'product_id')
    def validate_ids(cls, v):
        """Validate that IDs are non-empty strings."""
        v = v.strip()
        if not v:
            raise ValueError("ID cannot be empty")
        return v
    
    @validator('product_id')
    def validate_object_id(cls, v):
        """Validate that product_id is a valid ObjectId format."""
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid product ID format")
        return v


class OrderOut(BaseModel):
    """Schema for order response data."""
    
    id: str = Field(alias="_id", description="Order ID")
    user_id: str = Field(..., description="User ID who placed the order")
    product_id: str = Field(..., description="Product ID that was ordered")
    quantity: int = Field(..., description="Quantity ordered")
    created_at: datetime = Field(..., description="Order creation timestamp")
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
