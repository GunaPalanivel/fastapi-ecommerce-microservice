"""
Pydantic schemas for product data validation and serialization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic compatibility."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ProductIn(BaseModel):
    """Schema for product creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    size: List[str] = Field(..., min_items=1, description="Available sizes")
    available_quantity: int = Field(..., ge=0, description="Available quantity")
    
    @validator('size')
    def validate_sizes(cls, v):
        """Validate that sizes are non-empty strings."""
        if not v:
            raise ValueError("At least one size must be provided")
        
        valid_sizes = []
        for size in v:
            size = size.strip()
            if not size:
                raise ValueError("Size cannot be empty")
            valid_sizes.append(size.lower())
            
        return valid_sizes
    
    @validator('name')
    def validate_name(cls, v):
        """Validate and clean product name."""
        v = v.strip()
        if not v:
            raise ValueError("Product name cannot be empty")
        return v


class ProductOut(BaseModel):
    """Schema for product response data."""
    
    id: str = Field(alias="_id", description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    size: List[str] = Field(..., description="Available sizes")
    available_quantity: int = Field(..., description="Available quantity")
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
