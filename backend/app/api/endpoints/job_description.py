from fastapi import APIRouter, Depends
from app.models.db.job_description import JobDescriptionDB
from app.core.database import get_collections
from app.core.deps import get_current_workspace
from app.models.schema.fastapi.db_collections import Collections
from app.models.schema.fastapi.standard_response import StandardResponse, success_response
from app.models.schema.job_description.job_description_create import JobDescriptionCreate
from app.models.schema.session.session_workspace import SessionWorkspace
from app.core.logging import get_logger

router = APIRouter(prefix="", tags=["Job Description"])
logger = get_logger(__name__)


@router.post("/", response_model=StandardResponse[JobDescriptionDB])
async def create_job_description(
    jd_in: JobDescriptionCreate,
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    logger.info(
        f"Job description creation attempt by user_id={session.user_id}, workspace_id={session.workspace_id}, title={jd_in.job_title}"
    )

    jd = JobDescriptionDB(
        owner_id=session.user_id,
        workspace_id=session.workspace_id,
        **jd_in.dict(exclude_unset=True),
    )

    await collections.job_descriptions.insert_one(jd.model_dump())

    logger.info(
        f"Job description created successfully jd_id={jd.id}, user_id={session.user_id}, workspace_id={session.workspace_id}, title={jd.job_title}"
    )

    return success_response(jd)
