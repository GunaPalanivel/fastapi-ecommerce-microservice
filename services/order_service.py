"""
Order service layer handling business logic and database operations.
"""

import logging
from typing import List, Optional
from datetime import datetime

from bson import ObjectId

from db import get_collection
from schemas.order import OrderIn, OrderOut
from services.product_service import ProductService
from utils.pagination import PaginationParams

logger = logging.getLogger(__name__)


class OrderService:
    """Service class for order operations."""

    def __init__(self):
        self.collection = get_collection("orders")
        self.product_service = ProductService()

    async def create_order(self, order: OrderIn) -> OrderOut:
        """
        Create a new order in the database.
        Validates product existence and availability before creating the order.
        """
        try:
            logger.info(f"Validating product availability for product ID: {order.product_id}")

            product = await self.product_service.get_product_by_id(order.product_id)

            if not product:
                raise FileNotFoundError(f"Product with ID {order.product_id} not found")

            if product["available_quantity"] < order.quantity:
                raise ValueError(
                    f"Insufficient quantity. Available: {product['available_quantity']}, Requested: {order.quantity}"
                )

            order_doc = {
                "user_id": order.user_id,
                "product_id": order.product_id,
                "quantity": order.quantity,
                "created_at": datetime.utcnow()
            }

            logger.info(f"Inserting order for user {order.user_id}")
            result = await self.collection.insert_one(order_doc)

            if not result.inserted_id:
                raise ValueError("Failed to create order")

            logger.info(f"Updating product quantity for product ID: {order.product_id}")
            quantity_updated = await self.product_service.update_product_quantity(
                order.product_id, -order.quantity
            )

            if not quantity_updated:
                logger.warning("Product quantity update failed — rolling back order")
                await self.collection.delete_one({"_id": result.inserted_id})
                raise ValueError("Failed to update product quantity")

            created_order = await self.collection.find_one({"_id": result.inserted_id})
            logger.info(f"Order successfully created with ID: {created_order['_id']}")

            return OrderOut(
                _id=str(created_order["_id"]),
                user_id=created_order["user_id"],
                product_id=created_order["product_id"],
                quantity=created_order["quantity"],
                created_at=created_order["created_at"]
            )

        except (ValueError, FileNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {str(e)}", exc_info=True)
            raise ValueError("Failed to create order due to system error")

    async def list_user_orders(
        self,
        user_id: str,
        pagination: Optional[PaginationParams] = None
    ) -> List[OrderOut]:
        """
        Retrieve orders for a specific user with pagination.
        """
        try:
            logger.info(f"Fetching orders for user: {user_id}")
            query = {"user_id": user_id}
            cursor = self.collection.find(query).sort("created_at", -1)

            if pagination:
                cursor = cursor.skip(pagination.offset).limit(pagination.limit)

            orders = await cursor.to_list(length=None)
            logger.info(f"Found {len(orders)} orders for user {user_id}")

            return [
                OrderOut(
                    _id=str(order["_id"]),
                    user_id=order["user_id"],
                    product_id=order["product_id"],
                    quantity=order["quantity"],
                    created_at=order["created_at"]
                )
                for order in orders
            ]

        except Exception as e:
            logger.error(f"Error listing orders for user {user_id}: {str(e)}", exc_info=True)
            raise

    async def get_order_by_id(self, order_id: str) -> Optional[dict]:
        """
        Retrieve an order by its ID.
        """
        try:
            if not ObjectId.is_valid(order_id):
                logger.warning(f"Invalid ObjectId: {order_id}")
                return None

            logger.info(f"Retrieving order with ID: {order_id}")
            return await self.collection.find_one({"_id": ObjectId(order_id)})

        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}", exc_info=True)
            raise
