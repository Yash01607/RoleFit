from fastapi import APIRouter

from app.api.endpoints import auth, resume, job_description


def prepend_to_path(path: str):
    return f"/api{path}"


api_router = APIRouter()

api_router.include_router(auth.router, prefix=prepend_to_path(""), tags=["Auth"])
api_router.include_router(
    resume.router, prefix=prepend_to_path("/{workspace_id}/resume"), tags=["Resume"]
)
api_router.include_router(
    job_description.router,
    prefix=prepend_to_path("/{workspace_id}/jd"),
    tags=["Job Description"],
)
