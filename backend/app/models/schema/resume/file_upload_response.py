from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    message: str = "File Uploaded Successfully"
