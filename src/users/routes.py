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
from src.users.schema import UserResponse, RoleEnum
from src.users.users_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=UserResponse)
async def get_user_info_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user



# @router.patch("/{user_id}", response_model=UserResponse)
# async def update_user(
#     user_id: int,
#     current_user: User = Depends(get_current_user),
#     # user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
#     db: AsyncSession = Depends(get_db),
# ):
#     pass


# @router.post("/{user_id}", response_model=UserResponse)
# async def ban_user(
#     user_id: int,
#     current_user: User = Depends(get_current_user),
#     user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.USER])),
#     db: AsyncSession = Depends(get_db),
# ):
#     pass


# @router.post("/{user_id}", response_model=UserResponse)
# async def unban_user(
#     user_id: int,
#     current_user: User = Depends(get_current_user),
#     user: User = Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),
#     db: AsyncSession = Depends(get_db),
# ):
#     pass