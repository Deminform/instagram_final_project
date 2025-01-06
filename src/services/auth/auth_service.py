from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from conf.config import app_config
from conf.messages import (
    FORBIDDEN,
    INVALID_TOKEN_DATA,
    USER_NOT_FOUND,
    BANNED,
)
from database.db import get_db
from src.users.models import User
from src.users.repository import TokenRepository, UserRepository
from src.users.schemas import RoleEnum, TokenData


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# Generate token for verification email
def create_verification_token(email: EmailStr) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours=app_config.VERIFY_EMAIL_TOKEN_LIFETIME
    )
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(
        to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM
    )
    return encoded_jwt


def decode_verification_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, app_config.JWT_SECRET_KEY, algorithms=app_config.ALGORITHM
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email

    except JWTError:
        return None


#  Generate access token for user login
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM
    )
    return encoded_jwt


#  Generate refresh token to get new access token for user login
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=app_config.REFRESH_TOKEN_LIFETIME
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(
            token, app_config.JWT_SECRET_KEY, algorithms=app_config.ALGORITHM
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:

    # Check if token is provided in request
    token_data = decode_access_token(token)
    if token_data is None:
        raise UnauthorizedException(INVALID_TOKEN_DATA)

    # Check if user who sends request exists in db
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(token_data.username)
    if user is None:
        raise UnauthorizedException(USER_NOT_FOUND)

    # Check if provided token is active
    token_repo = TokenRepository(db)
    token_entry = await token_repo.get_active_token(user.id, token)
    if not token_entry:
        raise UnauthorizedException(INVALID_TOKEN_DATA)

    # Check if user isn't banned
    if user.is_banned:
        raise UnauthorizedException(BANNED)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> User:
        user = await get_current_user(token, db)

        if user.role.name not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=FORBIDDEN,
            )
        return user


class AuthService:
    def __init__(self, db: AsyncSession):
        self.token_repository = TokenRepository(db)

    async def add_tokens_db(
        self, user_id: int, access_token: str, refresh_token: str, status: bool
    ):
        return await self.token_repository.add_tokens(
            user_id, access_token, refresh_token, status
        )

    async def get_user_tokens(self, user_id: int) -> list:
        return await self.token_repository.get_user_tokens(user_id)

    async def delete_tokens(self, expired_tokens: list):
        return await self.token_repository.delete_tokens(expired_tokens)

    async def deactivate_user_tokens(self, user_id: int):
        return await self.token_repository.deactivate_user_tokens(user_id)
