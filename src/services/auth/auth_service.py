from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from conf.config import app_config
from conf.messages import FORBIDDEN, INCORRECT_CREDENTIALS
from database.db import get_db
from src.users.models import User
from src.users.repos import UserRepository
from src.users.schema import TokenData, RoleEnum


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Generate token for verification email
def create_verification_token(email: EmailStr) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=app_config.VERIFY_EMAIL_TOKEN_LIFETIME)
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM)
    return encoded_jwt


def decode_verification_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=app_config.ALGORITHM)
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
    encoded_jwt = jwt.encode(to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM)
    return encoded_jwt


#  Generate refresh token to get new access token for user login
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=app_config.REFRESH_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=app_config.ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INCORRECT_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    if user.is_banned:
        raise credentials_exception
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











def create_user():
    pass


def login():
    pass

def refresh_tokens():
    pass

def logout():
    pass

def verify_email():
    pass

def reset_password():
    pass