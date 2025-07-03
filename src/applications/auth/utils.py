"""
Модуль утилит по работе с паролями и токенов
- Хеширование пароля
- Валидация пароля
- Выпуск токена
- Декодирование токена
"""

from datetime import UTC, datetime, timedelta
import bcrypt
import jwt

from applications.auth.schemas import UserCreate
from core.conf import settings


_ACCESS_LIFETIME = timedelta(minutes=1)
_REFRESH_LIFETIME = timedelta(days=7)
_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"
_TOKEN_TYPE_FIELD = "token_type"


# ----------------------------- Пароли ----------------------------- #
def hash_password(password: str) -> str:
    """Принимаем пароль в виде строки и возвращаешь хеш в виде строки"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяешь пароль"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ----------------------------- Токены ------------------------------ #
def encode_jwt(
    payload: dict,
    secret_key: str = settings.secret_key,
    algorithm: str = settings.algorithm,
    refresh: bool = False,
):
    """Сгенерировать токен"""
    to_encode = payload.copy()
    now = datetime.now(UTC)
    exp = now + _ACCESS_LIFETIME if not refresh else now + _REFRESH_LIFETIME
    to_encode.update(exp=exp, iat=now)
    return jwt.encode(payload=to_encode, key=secret_key, algorithm=algorithm)


def decode_jwt(
    token: str,
    secret_key: str = settings.secret_key,
    algorithm: str = settings.algorithm,
):
    """Получить словарь из токена"""
    return jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])


def create_jwt(payload: dict, token_type: str, refresh: bool = False) -> str:
    jwt_payload = {_TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(payload)
    return encode_jwt(payload=jwt_payload, refresh=refresh)


def create_access_token(user: UserCreate):
    return create_jwt(
        payload={"sub": user.email, "id": user.id}, token_type=_ACCESS_TYPE
    )


def create_refresh_token(user: UserCreate):
    return create_jwt(
        payload={"sub": user.email}, token_type=_REFRESH_TYPE, refresh=True
    )
