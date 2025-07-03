"""
Модуль зависимостей для пользователя
"""

import jwt
from fastapi import Depends, Form, HTTPException
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
)
from pydantic import EmailStr
from starlette.requests import Request

from .utils import _ACCESS_TYPE, _TOKEN_TYPE_FIELD, _REFRESH_TYPE
from applications.auth.user_service import user_auth_service
from applications.auth.utils import decode_jwt, verify_password
from core.database import get_session

# _refresh_bearer = HTTPBearer(auto_error=False, description="Wait refresh token")
_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in", description="Root point login"
)


async def validate_auth_user(
    username: EmailStr = Form(), password: str = Form(), session=Depends(get_session)
):
    """Валидация пользователя по логину и паролю"""
    user = await user_auth_service.get_user(email=username, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(status_code=401, detail="Incorrect password or email")
    return user


def get_payload(token: str = Depends(_oauth2_scheme)):
    """Получить полезную нагрузку из токена"""
    try:
        payload = decode_jwt(token=token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")
    return payload


def check_token_type(payload: dict, token_type: str):
    if payload.get(_TOKEN_TYPE_FIELD) != token_type:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token type, expected '{token_type}' token type",
        )


async def _get_current_user_from_payload(payload: dict, session):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user = await user_auth_service.get_user(email=email, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_user(payload=Depends(get_payload), session=Depends(get_session)):
    """Получить текущего пользователя по токену"""
    check_token_type(payload, token_type=_ACCESS_TYPE)
    return await _get_current_user_from_payload(payload=payload, session=session)


async def get_current_user_for_refresh(
    payload=Depends(get_payload), session=Depends(get_session)
):
    check_token_type(payload, token_type=_REFRESH_TYPE)
    return await _get_current_user_from_payload(payload=payload, session=session)


# --------------------------------------------- alternative ---------------------------------------------
def get_payload_from_cookie(request: Request):
    """Получить полезную нагрузку из токена"""
    token = request.cookies.get("refresh_token")
    try:
        payload = decode_jwt(token=token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")
    return payload


async def get_current_user_for_refresh_from_cookie(
    payload=Depends(get_payload_from_cookie), session=Depends(get_session)
):
    check_token_type(payload, token_type=_REFRESH_TYPE)
    return await _get_current_user_from_payload(payload=payload, session=session)
