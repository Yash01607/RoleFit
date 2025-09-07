from fastapi import APIRouter, UploadFile, HTTPException, Depends, Path
from app.services.resume_service import parse_resume_bytes
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
from app.models.db.resume_parsed import ParsedResumeDB
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=StandardResponse[FileUploadResponse])
async def upload_resume(
    file: UploadFile,
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    if not is_pdf_file(file):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()

    if len(contents) > settings.MAX_UPLOAD_SIZE:
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

    return success_response(FileUploadResponse(file_id=metadata.id))


@router.post("/{resume_id}/parse", response_model=StandardResponse[ParsedResume])
async def upload_and_parse_resume(
    resume_id: str = Path(..., description="UUID of the uploaded resume"),
    collections: Collections = Depends(get_collections),
    session: SessionWorkspace = Depends(get_current_workspace),
):
    file_doc = await collections.resume_files_collection.find_one(
        {"metadata.id": resume_id, "metadata.workspace_id": session.workspace_id}
    )
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    already_parsed = collections.resume_parsed.find_one({"file_id": resume_id})

    if already_parsed:
        raise HTTPException(
            status_code=400,
            detail="This resume has already been parsed",
        )

    grid_out = await collections.resume_files.open_download_stream(file_doc["_id"])
    contents = await grid_out.read()
    parsed = parse_resume_bytes(contents)
    sections = {k: v for k, v in parsed.items()}

    _ = collections.resume_parsed.insert_one(
        ParsedResumeDB(
            file_id=resume_id,
            owner_id=session.user_id,
            workspace_id=session.workspace_id,
            sections=sections,
        ).model_dump()
    )

    return success_response(ParsedResume(sections=sections))
