from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException

from applications.auth.dependecies import validate_auth_user, get_current_user
from applications.auth.schemas import Token, UserCreate, UserLogin, User
from applications.auth.user_service import user_auth_service
from applications.auth.utils import encode_jwt
from core.database import get_session

router = APIRouter(prefix="/auth")

annotated_current_user = Annotated[User, Depends(get_current_user)]


@router.post("/sign-in")
async def login(user=Depends(validate_auth_user)) -> Token:
    token = encode_jwt(payload={"sub": user.email, "id": user.id})
    return Token(access_token=token)


@router.post("/sign-up")
async def register(user_in: UserCreate, session=Depends(get_session)):
    user = await user_auth_service.create(data=user_in, session=session)
    return user


@router.post("/sign-out")
async def logout():
    pass


@router.get("/auth/me", response_model_exclude={"created_at"})
async def profile(user: annotated_current_user) -> User:
    return user
