from app.models.schema.fastapi.db_collections import Collections
from app.models.db.workspace import WorkspaceDB
from app.models.schema.workspace.workspace_member import WorkspaceMember
from app.core.config import settings


async def create_default_workspace(
    user_id: str, collections: Collections
) -> WorkspaceDB:
    default_workspace = WorkspaceDB(
        name=settings.DEFAULT_WORKSPACE_NAME,
        members=[WorkspaceMember(user_id=user_id, is_admin=True)],
    )
    await collections.workspaces.insert_one(default_workspace.model_dump(by_alias=True))
    return default_workspace
