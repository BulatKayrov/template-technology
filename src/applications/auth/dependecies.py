"""
Модуль зависимостей для пользователя
"""

import jwt
from fastapi import Depends, Form, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from pydantic import EmailStr

from applications.auth.schemas import UserLogin
from applications.auth.user_service import user_auth_service
from applications.auth.utils import decode_jwt, verify_password
from core.database import get_session

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")


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


async def get_current_user(payload=Depends(get_payload), session=Depends(get_session)):
    """Получить текущего пользователя по токену"""
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user = await user_auth_service.get_user(email=email, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
