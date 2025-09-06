from app.models.schema.user.user_base import UserBase


class UserOut(UserBase):
    id: str
    is_superuser: bool
