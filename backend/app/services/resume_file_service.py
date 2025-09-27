from fastapi import HTTPException
from app.models.schema.fastapi.db_collections import Collections


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
