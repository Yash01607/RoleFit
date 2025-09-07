from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

from app.models.schema.fastapi.error_detail import ErrorDetail

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


def success_response(data: T) -> StandardResponse[T]:
    return StandardResponse[T](data=data)
