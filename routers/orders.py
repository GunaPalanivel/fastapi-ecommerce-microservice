"""
Order router handling all order-related endpoints.
Implements create and list operations with user-specific filtering.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query, Path, status

from schemas.order import OrderIn, OrderOut
from services.order_service import OrderService
from utils.pagination import PaginationParams

logger = logging.getLogger(__name__)
router = APIRouter(tags=["orders"])


@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=OrderOut)
async def create_order(order: OrderIn) -> OrderOut:
    """
    Create a new order in the system.
    """
    try:
        logger.info(f"Creating new order for user: {order.user_id}")
        
        service = OrderService()
        created_order = await service.create_order(order)

        logger.info(f"Order created successfully with ID: {created_order.id}")
        return created_order

    except ValueError as e:
        logger.warning(f"Order creation validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except FileNotFoundError as e:
        logger.warning(f"Product not found for order: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")


@router.get("/orders/{user_id}", status_code=status.HTTP_200_OK, response_model=List[OrderOut])
async def list_user_orders(
    user_id: str = Path(..., description="User ID to retrieve orders for"),
    limit: int = Query(10, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
) -> List[OrderOut]:
    """
    Retrieve a list of orders for a specific user with pagination.
    """
    try:
        logger.info(f"Listing orders for user: {user_id}")

        pagination = PaginationParams(limit=limit, offset=offset)
        service = OrderService()
        orders = await service.list_user_orders(user_id, pagination)

        logger.info(f"Retrieved {len(orders)} orders for user {user_id}")
        return orders

    except Exception as e:
        logger.error(f"Order listing failed for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve orders: {str(e)}")
