from app.models.schema.session.session_user import SessionUser


class SessionWorkspace(SessionUser):
    workspace_id: str
    is_current_user_admin: bool
