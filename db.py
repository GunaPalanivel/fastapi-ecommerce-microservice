"""
MongoDB database connection and configuration module.
Handles connection lifecycle and provides database access.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

load_dotenv()
logger = logging.getLogger(__name__)

# Global database connection
mongo_client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None

async def connect_to_mongo() -> None:
    """
    Establish connection to MongoDB.
    Creates indexes and validates collections.
    """
    global mongo_client, database

    try:
        mongo_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DATABASE_NAME", "ecommerce")

        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable is required")

        # MongoDB client with pool settings
        mongo_client = AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=45000,
            waitQueueMultiple=10,
            waitQueueTimeoutMS=10000
        )

        await mongo_client.admin.command("ping")  # Check connectivity
        database = mongo_client[db_name]

        await create_indexes()

        # Confirm seed data presence
        product_count = await database.products.count_documents({})
        order_count = await database.orders.count_documents({})
        logger.info(f"DB Connected: {db_name} | Products: {product_count} | Orders: {order_count}")

    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected DB error: {str(e)}")
        raise

async def create_indexes() -> None:
    """Create indexes for efficient querying."""
    if database is None:
        return

    try:
        await database.products.create_index("name")
        await database.products.create_index("size")
        await database.products.create_index([("name", "text")])

        await database.orders.create_index("user_id")
        await database.orders.create_index("product_id")
        await database.orders.create_index("created_at")
        await database.orders.create_index([("user_id", 1), ("created_at", -1)])

        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")

async def close_mongo_connection() -> None:
    """Gracefully close the MongoDB connection."""
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()
        logger.info("MongoDB connection closed")

def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    if database is None:
        raise ConnectionError("MongoDB not connected. Call connect_to_mongo() first.")
    return database

def get_collection(name: str):
    """Return a named collection from the active database."""
    return get_database()[name]
