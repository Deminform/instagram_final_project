from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr
from enum import Enum


class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"
    MODER = "moderator"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    avatar_url: str
    id: int
    role_name: Optional[str] = None
    is_confirmed: bool
    is_banned: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str