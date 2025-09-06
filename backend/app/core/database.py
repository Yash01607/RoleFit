# app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from fastapi import FastAPI
from fastapi import Request


async def connect_to_mongo(app: FastAPI):
    app.state.mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    app.state.mongo_db = app.state.mongo_client[settings.MONGO_DB]


async def close_mongo_connection(app: FastAPI):
    app.state.mongo_client.close()


def get_db(request: Request):
    return request.app.state.mongo_db
