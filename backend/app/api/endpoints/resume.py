from fastapi import APIRouter, UploadFile, HTTPException, Depends, Path
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
from app.utils.pdf.pdf_utils import is_pdf_file
from app.models.schema.resume.file_upload_response import FileUploadResponse
from app.core.deps import get_current_workspace
from app.models.schema.session.session_workspace import SessionWorkspace
from app.models.db.resume_metadata import ResumeMetadata
from app.core.config import settings
from app.services.resume_file_service import get_resume_file_contents
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

    if not is_pdf_file(file):
        logger.warning(
            f"Upload failed: Invalid file type filename={file.filename}, user_id={session.user_id}"
        )
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()

    if len(contents) > settings.MAX_UPLOAD_SIZE:
        logger.warning(
            f"Upload failed: File too large filename={file.filename}, size={len(contents)}, max={settings.MAX_UPLOAD_SIZE}, user_id={session.user_id}"
        )
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {settings.MAX_UPLOAD_SIZE} bytes",
        )

    metadata = ResumeMetadata(
        owner_id=session.user_id, workspace_id=session.workspace_id
    )

    await collections.resume_files.upload_from_stream_with_id(
        metadata.id,
        file.filename,
        contents,
        metadata=metadata.model_dump(),
    )

    logger.info(
        f"Resume uploaded successfully file_id={metadata.id}, filename={file.filename}, size={len(contents)}, user_id={session.user_id}, workspace_id={session.workspace_id}"
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
