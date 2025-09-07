from app.models.db.base import BaseModelDB


class WorkspaceMember(BaseModelDB):
    user_id: str
    is_admin: bool
