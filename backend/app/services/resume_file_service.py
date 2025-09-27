from typing import List
from fastapi import HTTPException, UploadFile, status
from app.models.schema.fastapi.db_collections import Collections
from app.core.logging import get_logger
from app.models.db.resume_metadata import ResumeMetadata
from app.models.schema.session.session_workspace import SessionWorkspace
from app.utils.pdf.pdf_utils import is_pdf_file
from app.core.config import settings
from app.models.schema.resume.resume_parsed import ParsedResume

logger = get_logger(__name__)


async def get_resume_file_contents(
    resume_id: str, workspace_id: str, collections: Collections
):
    file_doc = await collections.resume_files_collection.find_one(
        {"metadata.id": resume_id, "metadata.workspace_id": workspace_id}
    )
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    grid_out = await collections.resume_files.open_download_stream(file_doc["_id"])
    contents = await grid_out.read()

    return contents


async def upload_resume_file(
    file: UploadFile, session: SessionWorkspace, collections: Collections
) -> ResumeMetadata:
    if not is_pdf_file(file):
        logger.warning(
            f"Upload failed: Invalid file type filename={file.filename}, user_id={session.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed"
        )

    contents = await file.read()

    if len(contents) > settings.MAX_UPLOAD_SIZE:
        logger.warning(
            f"Upload failed: File too large filename={file.filename}, size={len(contents)}, max={settings.MAX_UPLOAD_SIZE}, user_id={session.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
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

    return metadata


async def get_resume_by_id(
    resume_id: str, session: SessionWorkspace, collections: Collections
) -> ParsedResume:

    doc = await collections.resume_parsed.find_one(
        {"id": resume_id, "workspace_id": session.workspace_id}
    )

    if not doc:
        logger.warning(
            f"Resume not found resume_id={resume_id}, user_id={session.user_id}, workspace_id={session.workspace_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    parsed_resume = ParsedResume(**doc)

    return parsed_resume


async def get_all_resumes(
    session: SessionWorkspace, collections: Collections
) -> List[ParsedResume]:

    cursor = collections.resume_parsed.find({"workspace_id": session.workspace_id})
    docs = await cursor.to_list(length=None)

    resumes = [ParsedResume(**doc) for doc in docs]

    return resumes
