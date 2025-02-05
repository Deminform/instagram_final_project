from typing import Sequence

from fastapi import APIRouter, Depends, File, UploadFile, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import USER_NOT_FOUND
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
    """
    Retrieve user information by user ID.
    :param user_id: The ID of the user to retrieve.
    :type user_id: int
    :param current_user: The current authenticated user, used to check permissions.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: User information response model.
    :rtype: UserResponse
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    return user


@router.get("/{username}/profile", response_model=UserResponse)
async def get_user_info_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve user information by username.
    :param username: The username of the user to retrieve.
    :type username: str
    :param current_user: The current authenticated user, used to check permissions.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: User information response model.
    :rtype: UserResponse
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND,
        )
    return user


@router.patch("/info", response_model=UserResponse)
async def update_user_info(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update user information.
    :param body: The updated user information.
    :type body: UserUpdate
    :param current_user: The current authenticated user, used to identify the user to update.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Updated user information.
    :rtype: User
    """
    user_service = UserService(db)
    user = await user_service.update_user(current_user.id, body)

    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_user_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update user avatar.
    :param file: The new avatar file to upload.
    :type file: UploadFile
    :param current_user: The current authenticated user, used to identify the user whose avatar is being updated.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Updated user information with the new avatar.
    :rtype: User
    """
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
    """
    Ban a user by ID (admin only).
    :param user_id: The ID of the user to ban.
    :type user_id: int
    :param current_user: The current authenticated user, required to have admin role.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Success message.
    :rtype: dict
    """
    user_service = UserService(db)
    await user_service.ban_user(user_id)
    return {"message": "Success"}


@router_admin.post("/{user_id}/unban", status_code=status.HTTP_200_OK, description="For 'admin' role only")
async def unban_user(
    user_id: int,
    current_user: User = Depends(
        RoleChecker([RoleEnum.ADMIN])
    ),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    """
    Unban a user by ID (admin only).
    :param user_id: The ID of the user to unban.
    :type user_id: int
    :param current_user: The current authenticated user, required to have admin role.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Success message.
    :rtype: dict
    """
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
    """
    Change the role of a user (admin only).
    :param user_id: The ID of the user whose role is to be changed.
    :type user_id: int
    :param role: The new role to assign to the user.
    :type role: str
    :param current_user: The current authenticated user, required to have admin role.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Success message.
    :rtype: dict
    """
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
    """
    Search for users based on various parameters.
    :param search_param: Search term for first name, last name, or email.
    :type search_param: str | None
    :param has_posts: Whether to filter users who have posts.
    :type has_posts: bool | None
    :param offset: The offset for pagination.
    :type offset: int
    :param limit: The number of users to return (pagination).
    :type limit: int
    :param current_user: The current authenticated user, required to have admin or moderator role.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of users matching the search criteria.
    :rtype: Sequence[UserResponse]
    """
    user_service = UserService(db)
    users = await user_service.search_users(search_param, has_posts, offset, limit)
    return users

