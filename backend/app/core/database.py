from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.schema.fastapi.db_collections import Collections
from app.models.schema.fastapi.app_state import AppState


async def connect_to_mongo(app: FastAPI):
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.MONGO_DB]

    state: AppState = app.state
    state.mongo_client = client
    state.mongo_db = db
    state.collections = Collections(db)


async def close_mongo_connection(app: FastAPI):
    state: AppState = app.state
    state.mongo_client.close()


def get_collections(request: Request) -> Collections:
    state: AppState = request.app.state
    return state.collections
