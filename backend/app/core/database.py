from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    global client, db
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.MONGO_DB]
    logger.info("Connected to MongoDB at %s", settings.mongo_uri)


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
