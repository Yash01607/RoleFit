from datetime import timedelta
from fastapi import HTTPException
from app.core.config import settings
from app.models.db.user import UserDB
from app.models.schema.user.user_create import UserCreate
from app.utils.auth.security import hash_password, verify_password
from app.utils.auth.jwt import create_access_token
from app.models.schema.fastapi.db_collections import Collections


async def create_user(user: UserCreate, collections: Collections) -> UserDB:
    if user.password1 != user.password2:
        raise HTTPException(
            status_code=400, detail="Password and Confirm Password must be same"
        )
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password1"))
    new_user = UserDB(**user_dict)
    await collections.users.insert_one(new_user.dict(by_alias=True))
    return new_user


async def authenticate_user(
    email: str, password: str, collections: Collections
) -> UserDB | None:
    user_data = await collections.users.find_one({"email": email})
    if not user_data:
        return None
    user = UserDB(**user_data)
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: UserDB) -> str:
    """Generate JWT token for authenticated user with role info."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": str(user.id), "is_superuser": user.is_superuser}
    return create_access_token(data=token_data, expires_delta=access_token_expires)
