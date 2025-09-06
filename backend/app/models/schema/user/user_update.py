
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
