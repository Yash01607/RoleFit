from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password1: str
    password2: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
