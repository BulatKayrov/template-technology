"""
Модуль auth сервис
Реализация сервиса по работе с таблицей пользователей
"""

from fastapi import HTTPException, status
from sqlalchemy import select

from applications.auth.schemas import UserCreate, UserUpdate
from applications.auth.utils import hash_password
from core.database import BaseRepository
from typing import Annotated, TYPE_CHECKING

from core.database.models import User

if TYPE_CHECKING:

    from sqlalchemy.ext.asyncio import AsyncSession


class UserService(BaseRepository):

    async def create(
        self,
        data: UserCreate,
        session: "AsyncSession",
    ) -> "User":
        if data.password1 != data.password2:
            raise HTTPException(status_code=400, detail="Passwords don't match")
        password = hash_password(data.password1)
        data = data.model_dump(exclude_none=True, exclude_unset=True)
        user = User(
            password=password,
            fullname=data["fullname"],
            phone=data["phone"],
            email=data["email"],
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def find_all(self, user: User, session: "AsyncSession"):
        if user.is_admin:
            res = await session.execute(select(User))
            return res.scalars().all()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="доступно только администраторам",
        )

    async def delete(self, user: User, session: "AsyncSession"):
        user.is_active = False
        await session.commit()
        await session.refresh(user)
        return user

    async def update(
        self,
        user_in: User,
        data: UserUpdate,
        session: "AsyncSession",
    ):
        for k, v in data.model_dump(exclude_none=True, exclude_unset=True):
            setattr(user_in, k, v)
        await session.commit()
        await session.refresh(user_in)
        return user_in

    async def get_user(
        self,
        email: str,
        session: "AsyncSession",
    ):
        res = await session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()


user_auth_service = UserService()
