from app.models.db.base import BaseModelDB


class ResumeMetadata(BaseModelDB):
    owner_id: str
    workspace_id: str
