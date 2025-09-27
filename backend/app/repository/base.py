from typing import Any, Generic, TypeVar, Optional, Dict
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection: AsyncIOMotorCollection = collection

    async def get(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single document matching the filter"""
        return await self.collection.find_one(filter)

    async def insert(self, data: Dict[str, Any]) -> str:
        """Insert a new document and return its ID"""
        result: InsertOneResult = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def update(
        self, filter: Dict[str, Any], update_data: Dict[str, Any]
    ) -> UpdateResult:
        """Update a document matching the filter"""
        result: UpdateResult = await self.collection.update_one(
            filter, {"$set": update_data}
        )
        return result

    async def delete(self, filter: Dict[str, Any]) -> DeleteResult:
        """Delete a document matching the filter"""
        result: DeleteResult = await self.collection.delete_one(filter)
        return result
