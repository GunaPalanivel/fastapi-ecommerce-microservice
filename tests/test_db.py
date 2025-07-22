import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    load_dotenv()
    
    mongo_uri = os.getenv("MONGODB_URI")
    print(f"Connecting to: {mongo_uri[:50]}...")
    
    try:
        client = AsyncIOMotorClient(mongo_uri)
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client[os.getenv("DATABASE_NAME", "ecommerce")]
        collections = await db.list_collection_names()
        print(f"✅ Database accessible. Collections: {collections}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        client.close()

# Run the test
asyncio.run(test_connection())
