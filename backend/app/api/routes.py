from fastapi import APIRouter

from app.api.endpoints import auth


def prepend_to_path(path: str):
    return f"/api{path}"


api_router = APIRouter()

api_router.include_router(auth.router, prefix=prepend_to_path(""), tags=["Auth"])
