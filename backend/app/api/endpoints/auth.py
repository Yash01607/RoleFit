from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.models.schema.user.user_create import UserCreate
from app.models.schema.user.user_out import UserOut
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_token_for_user,
)
from app.models.schema.general.standard_response import (
    StandardResponse,
    success_response,
)
from app.models.schema.user.login_response import LoginResponse

router = APIRouter()


@router.post("/signup", response_model=StandardResponse[UserOut])
async def signup(user: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_user = await create_user(user, db)
    return success_response(UserOut(**new_user.model_dump()))


@router.post("/login", response_model=StandardResponse[LoginResponse])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """
    Login endpoint using OAuth2PasswordRequestForm.
    Returns JWT token.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_token_for_user(user)
    return success_response(LoginResponse(access_token=token, token_type="bearer"))
