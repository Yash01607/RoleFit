from fastapi import APIRouter

from app.api.endpoints import auth, resume


def prepend_to_path(path: str):
    return f"/api{path}"


api_router = APIRouter()

api_router.include_router(auth.router, prefix=prepend_to_path(""), tags=["Auth"])
api_router.include_router(
    resume.router, prefix=prepend_to_path("/{workspace_id}/resume"), tags=["Resume"]
)
