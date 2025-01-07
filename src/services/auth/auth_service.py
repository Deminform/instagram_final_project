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
    """
    Provides methods for password hashing and verification using bcrypt.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the provided plain password matches the hashed password.

        :param plain_password: Plain text password to be verified.
        :type plain_password: str
        :param hashed_password: Hashed password to compare with.
        :type hashed_password: str
        :return: True if passwords match, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generate a hash for the provided password.

        :param password: Password to be hashed.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
"""
OAuth2 schema to be used for authentication token in the requests.
"""

# Generate token for verification email
def create_verification_token(email: EmailStr) -> str:
    """
    Create a token for email verification.

    :param email: Email address for which to create the verification token.
    :type email: EmailStr
    :return: JWT token for email verification.
    :rtype: str
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=app_config.VERIFY_EMAIL_TOKEN_LIFETIME
    )
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(
        to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM
    )
    return encoded_jwt


def decode_verification_token(token: str) -> str | None:
    """
    Decode the verification token to retrieve the email.

    :param token: The token to decode.
    :type token: str
    :return: The email if the token is valid, None if invalid.
    :rtype: str | None
    """
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
    """
    Generate an access token for the user.

    :param data: Data to be encoded in the access token.
    :type data: dict
    :return: JWT access token.
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.ALGORITHM
    )
    return encoded_jwt


#  Generate refresh token to get new access token for user login
def create_refresh_token(data: dict):
    """
    Generate a refresh token for obtaining a new access token.

    :param data: Data to be encoded in the refresh token.
    :type data: dict
    :return: JWT refresh token.
    :rtype: str
    """
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
    """
    Decode the access token to retrieve the user data.

    :param token: The token to decode.
    :type token: str
    :return: The user data if the token is valid, None if invalid.
    :rtype: TokenData | None
    """
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
    """
    Retrieve the current user based on the provided token.

    :param token: Access token to authenticate the user.
    :type token: str
    :param db: Database session.
    :type db: AsyncSession
    :return: User object if the token is valid and the user exists.
    :rtype: User
    :raises UnauthorizedException: If the token is invalid or the user is not found.
    """
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
    """
    Class for checking if the user has the required role for accessing certain resources.
    """
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Checks if the user has the required role to access the resource.

        :param token: Access token for authentication.
        :type token: str
        :param db: Database session.
        :type db: AsyncSession
        :return: User object if the user's role is allowed.
        :rtype: User
        :raises HTTPException: If the user's role is not allowed.
        """
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
        """
        Adds access and refresh tokens for the user to the database.

        :param user_id: User ID for which tokens are added.
        :type user_id: int
        :param access_token: Access token to be added.
        :type access_token: str
        :param refresh_token: Refresh token to be added.
        :type refresh_token: str
        :param status: The status of the tokens (active or inactive).
        :type status: bool
        :return: Result of the token addition operation.
        :rtype: Any
        """
        return await self.token_repository.add_tokens(
            user_id, access_token, refresh_token, status
        )

    async def get_user_tokens(self, user_id: int) -> list:
        """
        Retrieves all tokens of the user from the database.

        :param user_id: User ID for which tokens are retrieved.
        :type user_id: int
        :return: List of tokens associated with the user.
        :rtype: list
        """
        return await self.token_repository.get_user_tokens(user_id)

    async def delete_tokens(self, expired_tokens: list):
        """
        Deletes expired tokens from the database.

        :param expired_tokens: List of expired tokens to be deleted.
        :type expired_tokens: list
        :return: Result of the deletion operation.
        :rtype: Any
        """
        return await self.token_repository.delete_tokens(expired_tokens)

    async def deactivate_user_tokens(self, user_id: int):
        """
        Deactivates all tokens of the user.

        :param user_id: User ID for which tokens are deactivated.
        :type user_id: int
        :return: Result of the token deactivation operation.
        :rtype: Any
        """
        return await self.token_repository.deactivate_user_tokens(user_id)
