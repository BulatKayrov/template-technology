from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    fullname: str | None
    phone: str | None
    email: EmailStr


class UserCreate(UserBase):
    password1: str
    password2: str


class UserUpdate(UserBase):
    fullname: str | None = None
    phone: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime | None
    updated_at: datetime | None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
