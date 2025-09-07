from typing import List
from app.models.db.base import BaseModelDB
from app.models.schema.workspace.workspace_member import WorkspaceMember


class WorkspaceDB(BaseModelDB):
    name: str
    description: str = ""
    members: List[WorkspaceMember]
