from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.logging import get_logger
from app.core.database import Collections, get_collections
from app.models.schema.user.user_create import UserCreate
from app.models.schema.user.user_out import UserOut
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_token_for_user,
)
from app.models.schema.fastapi.standard_response import (
    StandardResponse,
    success_response,
)
from app.services.workspace_service import create_default_workspace
from app.services.user_service import update_user
from app.models.schema.user.user_update import UserUpdate

logger = get_logger(__name__)

router = APIRouter()


@router.post("/signup", response_model=StandardResponse[UserOut])
async def signup(user: UserCreate, collections: Collections = Depends(get_collections)):
    logger.info(f"Signup attempt for email={user.email}")

    existing_user = await collections.users.find_one({"email": user.email})
    if existing_user:
        logger.warning(f"Signup failed: User already exists email={user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_user = await create_user(user, collections)
    logger.info(f"User created successfully user_id={new_user.id}, email={new_user.email}")

    default_workspace = await create_default_workspace(new_user.id, collections)
    _ = await update_user(
        user_id=new_user.id,
        update_data=UserUpdate(primary_workspace_id=default_workspace.id),
        collections=collections,
    )

    logger.info(
        f"Default workspace created workspace_id={default_workspace.id}, user_id={new_user.id}"
    )

    return success_response(
        UserOut(
            workspace_id=default_workspace.id,
            workspace_name=default_workspace.name,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            id=new_user.id,
            is_superuser=new_user.is_superuser,
        )
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    collections: Collections = Depends(get_collections),
):
    logger.info(f"Login attempt for username={form_data.username}")

    user = await authenticate_user(form_data.username, form_data.password, collections)
    if not user:
        logger.warning(f"Login failed for username={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_token_for_user(user)
    logger.info(f"Login successful for user_id={user.id}, email={user.email}")

    return {"access_token": token, "token_type": "bearer"}
