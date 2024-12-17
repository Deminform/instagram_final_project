from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import (ACCOUNT_EXIST, EMAIL_ALREADY_CONFIRMED, EMAIL_CONFIRMED, EMAIL_NOT_CONFIRMED,
                           INCORRECT_CREDENTIALS, USER_NOT_FOUND)
from database.db import get_db
from src.users.mail_utils import send_verification_email
from src.users.pass_utils import verify_password
from src.users.repos import UserRepository
from src.users.schema import UserResponse, UserCreate, Token
from src.users.utils import decode_verification_token, create_access_token, create_refresh_token, decode_access_token

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ACCOUNT_EXIST,
        )
    user = await user_repo.get_user_by_username(user_create.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ACCOUNT_EXIST,
        )
    user = await user_repo.create_user(user_create)
    background_tasks.add_task(send_verification_email, user.email, request.base_url)
    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email: str = decode_verification_token(token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND,
        )
    if user.is_confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await user_repo.activate_user(user)
    return {"msg": EMAIL_CONFIRMED}


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INCORRECT_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    refresh_token: str, db: AsyncSession = Depends(get_db)
) -> Token:
    token_data = decode_access_token(refresh_token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INCORRECT_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )