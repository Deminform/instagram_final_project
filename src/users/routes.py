from fastapi import (
    APIRouter,
    Depends,
    HTTPException, status
)
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import USER_NOT_FOUND
from database.db import get_db
from src.services.auth.auth_service import get_current_user, RoleChecker
from src.users.models import User
from src.users.repos import UserRepository
from src.users.schema import UserResponse, RoleEnum

router = APIRouter(prefix="/users", tags=["users"])


# @router.get("/{username}", response_model=UserResponse)
# async def get_current_user_info(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     return current_user

@router.get("/{username}", response_model=UserResponse)
async def get_current_user_info(
    username: str,
    current_user: User = Depends(get_current_user),
    # user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user



@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    # user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
    db: AsyncSession = Depends(get_db),
):
    pass


@router.post("/{user_id}", response_model=UserResponse)
async def ban_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
    db: AsyncSession = Depends(get_db),
):
    pass


@router.post("/{user_id}", response_model=UserResponse)
async def unban_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass