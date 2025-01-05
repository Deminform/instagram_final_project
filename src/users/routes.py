from typing import Sequence

from fastapi import APIRouter, Depends, File, UploadFile, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from src.services.auth.auth_service import RoleChecker, get_current_user
from src.users.models import User
from src.users.schemas import RoleEnum, UserResponse, UserUpdate
from src.users.users_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
router_admin = APIRouter(prefix="/admin/user", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    return user


@router.get("/{username}/profile", response_model=UserResponse)
async def get_user_info_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    return user


@router.patch("/info", response_model=UserResponse)
async def update_user_info(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_service = UserService(db)
    user = await user_service.update_user(current_user.id, body)

    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_user_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_service = UserService(db)
    user = await user_service.update_avatar(current_user.username, file)

    return user


# ------------- ADMIN ROUTES -----------------------------------
@router_admin.post("/{user_id}/ban", status_code=status.HTTP_200_OK, description="For 'admin' role only")
async def ban_user(
    user_id: int,
    current_user: User = Depends(
        RoleChecker([RoleEnum.ADMIN])
    ),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.ban_user(user_id)
    return {"message": "Success"}


@router_admin.post("/{user_id}/unban", status_code=status.HTTP_200_OK, description="For 'admin' role only")
async def ban_user(
    user_id: int,
    current_user: User = Depends(
        RoleChecker([RoleEnum.ADMIN])
    ),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.unban_user(user_id)
    return {"message": "Success"}


@router_admin.patch("/{user_id}/role", status_code=status.HTTP_200_OK, description="For 'admin' role only")
async def change_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(
        RoleChecker([RoleEnum.ADMIN])
    ),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.change_role(user_id, role)
    return {"message": "Success"}


@router_admin.get("/search", response_model=Sequence[UserResponse], status_code=status.HTTP_200_OK)
async def search_users(
        search_param: str = Query(None, description="Search by first name or last name or email"),
        has_posts: bool = None,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=10, le=100, ge=10),
        current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MODER])),  # TODO Check admin permission
        db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    users = await user_service.search_users(search_param, has_posts, offset, limit)
    return users

