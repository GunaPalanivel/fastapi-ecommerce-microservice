"""
Pagination utilities for consistent pagination across the application.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters with validation."""
    
    limit: int = Field(default=10, ge=1, le=100, description="Number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    
    @property
    def skip(self) -> int:
        """Alias for offset for MongoDB compatibility."""
        return self.offset


class PaginationMeta(BaseModel):
    """Pagination metadata for responses."""
    
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Items skipped")
    has_next: bool = Field(..., description="Whether there are more items")
    has_previous: bool = Field(..., description="Whether there are previous items")
    
    @classmethod
    def create(cls, total: int, pagination: PaginationParams) -> "PaginationMeta":
        """Create pagination metadata from total count and parameters."""
        return cls(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_next=pagination.offset + pagination.limit < total,
            has_previous=pagination.offset > 0
        )


def calculate_skip_limit(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None
) -> PaginationParams:
    """
    Calculate skip and limit from various pagination parameters.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        offset: Items to skip (0-based)
        limit: Items to return
        
    Returns:
        PaginationParams with calculated offset and limit
    """
    if page is not None and per_page is not None:
        # Convert page-based pagination to offset-based
        calculated_offset = (page - 1) * per_page
        calculated_limit = per_page
    else:
        # Use offset/limit directly
        calculated_offset = offset or 0
        calculated_limit = limit or 10
    
    return PaginationParams(offset=calculated_offset, limit=calculated_limit)
