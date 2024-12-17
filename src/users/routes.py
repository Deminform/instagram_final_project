from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import ACCOUNT_EXIST, EMAIL_ALREADY_CONFIRMED, EMAIL_CONFIRMED
from database.db import get_db
from src.users.mail_utils import send_verification_email
from src.users.repos import UserRepository
from src.users.schema import UserResponse, UserCreate
from src.users.utils import decode_verification_token

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
            detail="User not found",
        )
    if user.is_confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await user_repo.activate_user(user)
    return {"msg": EMAIL_CONFIRMED}

