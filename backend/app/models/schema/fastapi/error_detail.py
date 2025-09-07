from pydantic import BaseModel
from datetime import datetime


class ErrorDetail(BaseModel):
    timestamp: datetime
    status_code: int
    detail: str
    endpoint: str
