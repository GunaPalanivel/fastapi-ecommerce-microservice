import asyncio
import os
import random
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone


load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME", "fastapi-ecommerce-microservice")

sample_products = [
    {"name": "Gaming Laptop", "price": 1299.99, "size": ["large"], "available_quantity": 10},
    {"name": "Wireless Mouse", "price": 29.99, "size": ["small"], "available_quantity": 50},
    {"name": "Office Chair", "price": 199.99, "size": ["large"], "available_quantity": 20},
    {"name": "Noise Cancelling Headphones", "price": 299.99, "size": ["medium"], "available_quantity": 25},
    {"name": "Mechanical Keyboard", "price": 89.99, "size": ["medium"], "available_quantity": 40},
    {"name": "Monitor 24in", "price": 149.99, "size": ["large"], "available_quantity": 15},
    {"name": "USB-C Hub", "price": 49.99, "size": ["small"], "available_quantity": 30},
    {"name": "External SSD", "price": 159.99, "size": ["small"], "available_quantity": 35},
    {"name": "Smartwatch", "price": 199.99, "size": ["small"], "available_quantity": 18},
    {"name": "Portable Speaker", "price": 79.99, "size": ["medium"], "available_quantity": 22},
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["fastapi-ecommerce-microservice"]

    # Wipe existing data
    await db.products.delete_many({})
    await db.orders.delete_many({})

    # Insert products
    result = await db.products.insert_many(sample_products)
    print(f"✅ Inserted {len(result.inserted_ids)} products.")

    # Insert flat orders (user_id, product_id, quantity)
    count = 0
    for i in range(10):  # 10 users
        user_id = f"user_{i}"
        for _ in range(random.randint(1, 3)):
            product_id = str(random.choice(result.inserted_ids))
            quantity = random.randint(1, 5)
            await db.orders.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "created_at": datetime.now(timezone.utc)
   })
            count += 1

    print(f"✅ Inserted {count} orders.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
