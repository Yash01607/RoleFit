from typing import List
from fastapi import APIRouter, UploadFile, Depends, Path
from app.services.resume_service import (
    get_sections_from_resume,
    is_resume_parsed,
    insert_parsed_resume,
)
from app.models.schema.fastapi.standard_response import (
    StandardResponse,
    success_response,
)
from app.models.schema.resume.resume_parsed import ParsedResume
from app.core.database import get_collections
from app.models.schema.fastapi.db_collections import Collections
from app.models.schema.resume.file_upload_response import FileUploadResponse
from app.core.deps import get_current_workspace
from app.models.schema.session.session_workspace import SessionWorkspace
from app.services.resume_file_service import (
    get_all_resumes,
    get_resume_by_id,
    get_resume_file_contents,
    upload_resume_file,
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=StandardResponse[FileUploadResponse])
async def upload_resume(
    file: UploadFile,
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    logger.info(
        f"Resume upload attempt user_id={session.user_id}, workspace_id={session.workspace_id}, filename={file.filename}"
    )

    metadata = await upload_resume_file(file, session, collections)

    logger.info(
        f"Resume uploaded successfully file_id={metadata.id}, filename={file.filename}, user_id={session.user_id}, workspace_id={session.workspace_id}"
    )

    return success_response(FileUploadResponse(file_id=metadata.id))


@router.post("/{resume_id}/parse", response_model=StandardResponse[ParsedResume])
async def upload_and_parse_resume(
    resume_id: str = Path(..., description="UUID of the uploaded resume"),
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    logger.info(
        f"Resume parse attempt resume_id={resume_id}, user_id={session.user_id}, workspace_id={session.workspace_id}"
    )

    contents = await get_resume_file_contents(
        resume_id, session.workspace_id, collections
    )

    is_resume_parsed(resume_id, collections)

    sections = get_sections_from_resume(contents)

    await insert_parsed_resume(
        resume_id, session.user_id, session.workspace_id, sections, collections
    )

    logger.info(
        f"Resume parsed successfully resume_id={resume_id}, user_id={session.user_id}, workspace_id={session.workspace_id}, sections_count={len(sections)}"
    )

    return success_response(ParsedResume(sections=sections))


@router.get("/{resume_id}", response_model=StandardResponse[ParsedResume])
async def get_resume_by_id_handler(
    resume_id: str = Path(..., description="UUID of the resume"),
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    logger.info(
        f"Get resume by id attempt resume_id={resume_id}, user_id={session.user_id}, workspace_id={session.workspace_id}"
    )

    parsed_resume = await get_resume_by_id(resume_id, session, collections)

    logger.info(
        f"Resume fetched successfully resume_id={resume_id}, user_id={session.user_id}, workspace_id={session.workspace_id}"
    )

    return success_response(parsed_resume)


@router.get("/", response_model=StandardResponse[List[ParsedResume]])
async def get_all_resumes_handler(
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    logger.info(
        f"Get all resumes attempt user_id={session.user_id}, workspace_id={session.workspace_id}"
    )

    resumes = await get_all_resumes(session, collections)

    logger.info(
        f"Fetched {len(resumes)} resumes for workspace_id={session.workspace_id}, user_id={session.user_id}"
    )

    return success_response(resumes)
