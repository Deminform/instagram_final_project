from datetime import datetime
from enum import Enum
from typing import Optional
from typing_extensions import Annotated
import re

from pydantic import BaseModel, EmailStr, BeforeValidator

from src.users.models import User


class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"
    MODER = "moderator"


def validate_phone(phone: str) -> str:
    phone_regex = r"^\+?[1-9]\d{9,14}$"
    if not re.match(phone_regex, phone):
        raise ValueError("Invalid phone number format")
    return phone


class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone: Annotated[str, BeforeValidator(validate_phone)]
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    avatar_url: str
    id: int
    phone: Optional[str] = None
    role_name: Optional[str] = None
    post_count: Optional[int] = None
    is_confirmed: bool
    is_banned: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True

    @classmethod
    def from_user(cls, user: User, post_count: int = 0) -> "UserResponse":
        return cls(
            **user.__dict__,
            role_name=user.role.name if user.role else None,
            post_count=post_count,
        )

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Annotated[Optional[str], BeforeValidator(validate_phone)] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime
