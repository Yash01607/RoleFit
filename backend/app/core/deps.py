# app/services/auth_service.py
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from app.core.database import get_collections
from app.models.schema.fastapi.db_collections import Collections
from app.utils.auth.jwt import verify_access_token
from app.models.schema.session.session_user import SessionUser
from app.models.schema.session.session_workspace import SessionWorkspace
from app.models.db.workspace import WorkspaceDB
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    collections: Collections = Depends(get_collections),
):
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = await collections.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return SessionUser(
        user_id=str(user["_id"]),
        email=user.get("email"),
    )


async def get_current_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    collections: Collections = Depends(get_collections),
    current_user: SessionUser = Depends(get_current_user),
):
    workspace = await collections.workspaces.find_one(
        {"_id": workspace_id}
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    workspace = WorkspaceDB(**workspace)

    member = next(
        (m for m in workspace.members if m.user_id == current_user.user_id),
        None,
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace",
        )

    return SessionWorkspace(
        user_id=current_user.user_id,
        email=current_user.user_id,
        workspace_id=workspace_id,
        is_current_user_admin=member.is_admin,
    )
