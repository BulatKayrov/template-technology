from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from applications.auth.dependecies import (
    # _refresh_bearer,
    # get_current_user_for_refresh,
    get_current_user_for_refresh_from_cookie,
    validate_auth_user,
    get_current_user,
)
from applications.auth.schemas import Token, UserCreate, User
from applications.auth.user_service import user_auth_service
from applications.auth.utils import (
    create_access_token,
    create_refresh_token,
)
from core.database import get_session

router = APIRouter(prefix="/auth")
annotated_current_user = Annotated[User, Depends(get_current_user)]


@router.post("/sign-in")
async def login(response: Response, user=Depends(validate_auth_user)) -> Token:
    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True
    )
    response.headers["Authorization"] = f"Bearer {access_token}"
    return Token(access_token=access_token)


@router.post("/sign-up")
async def register(user_in: UserCreate, session=Depends(get_session)):
    user = await user_auth_service.create(data=user_in, session=session)
    return user


@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def refresh_token_view(
    response: Response,
    user=Depends(get_current_user_for_refresh_from_cookie),
):
    access_token = create_access_token(user=user)
    response.headers["Authorization"] = f"Bearer {access_token}"
    return Token(access_token=access_token)


@router.post("/logout")
async def logout_view(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"success": True}


@router.get("/auth/me", response_model_exclude={"created_at"})
async def profile(user: annotated_current_user) -> User:
    return user
