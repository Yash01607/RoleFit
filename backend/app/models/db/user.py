from typing import Optional
from app.models.db.base import BaseModelDB


class UserDB(BaseModelDB):
    email: str
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: bool = False
