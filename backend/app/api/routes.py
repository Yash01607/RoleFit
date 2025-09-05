from fastapi import APIRouter

from app.api.endpoints import user


def prepend_to_path(path: str):
    return f"/api{path}"


api_router = APIRouter()

api_router.include_router(user.router, prefix=prepend_to_path(""), tags=["User"])
