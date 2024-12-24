from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from conf.config import app_config
from conf.messages import (
    ACCOUNT_EXIST,
    BANNED,
    EMAIL_ALREADY_CONFIRMED,
    EMAIL_CONFIRMED,
    EMAIL_NOT_CONFIRMED,
    INCORRECT_CREDENTIALS,
    USER_NOT_FOUND, LOGOUT_SUCCESS,
)
from database.db import get_db
from src.services.auth.auth_service import (
    Hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_verification_token,
    get_current_user, AuthService,
)
from src.services.auth.mail_utils import send_verification_email
from src.users.models import User
from src.users.schema import Token, UserCreate, UserResponse
from src.users.users_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ACCOUNT_EXIST,
        )
    user = await user_service.get_user_by_username(user_create.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ACCOUNT_EXIST,
        )
    user = await user_service.create_user(user_create)
    background_tasks.add_task(send_verification_email, user.email, request.base_url)
    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email: str = decode_verification_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND,
        )
    if user.is_confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await user_service.activate_user(user)
    return {"message": EMAIL_CONFIRMED}


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:
    user_service = UserService(db)
    user = await user_service.get_user_by_email(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INCORRECT_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED)
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=BANNED)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    auth_service = AuthService(db)
    await auth_service.add_tokens_db(user.id, access_token, refresh_token, status=True)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)) -> Token:
    token_data = decode_access_token(refresh_token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(token_data.username)
    if not user or user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INCORRECT_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.get("/logout")
async def logout(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):

    user_service = UserService(db)
    user = await user_service.get_user_by_email(current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND,
        )
    auth_service = AuthService(db)
    token_records = await auth_service.get_user_tokens(user.id)
    expired_tokens = []
    for record in token_records:
        if (
            datetime.now() - record.created_at
        ).days > app_config.REFRESH_TOKEN_LIFETIME:
            expired_tokens.append(record.id)
            print("record", record.id)
    if expired_tokens:
        await auth_service.delete_tokens(expired_tokens)

    await auth_service.deactivate_user_tokens(user.id)
    return {"message": LOGOUT_SUCCESS}


