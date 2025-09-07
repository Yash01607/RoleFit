from starlette.datastructures import State
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from app.models.schema.fastapi.db_collections import Collections


class AppState(State):
    mongo_client: AsyncIOMotorClient
    mongo_db: AsyncIOMotorDatabase
    collections: Collections
