from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File, HTTPException, status
)
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import USER_NOT_FOUND
from database.db import get_db
from conf.config import app_config
from src.auth.models import User
from src.auth.repos import UserRepository
from src.auth.schema import UserResponse, RoleEnum
from src.auth.utils import get_current_user, RoleChecker

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return current_user

@router.get("/user{user_id}", response_model=UserResponse)
async def get_current_user_info(
    user_id: int,
    user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user

