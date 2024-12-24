import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from conf.config import app_config
from conf.messages import USER_NOT_FOUND
from database.db import get_db
from src.services.auth.auth_service import RoleChecker, get_current_user
from src.users.models import User
from src.users.schema import RoleEnum, UserResponse, UserUpdate
from src.users.users_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


@router.get("/{username}/profile", response_model=UserResponse)
async def get_user_info_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


@router.patch("/info", response_model=UserResponse)
async def update_user_info(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_service = UserService(db)
    user = await user_service.update_user(current_user.id, body)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_user_info(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    cloudinary.config(
        cloud_name=app_config.CLOUDINARY_NAME,
        api_key=app_config.CLOUDINARY_API_KEY,
        api_secret=app_config.CLOUDINARY_API_SECRET,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"Inst_project/{current_user.username}", overwrite=True
    )

    src_url = cloudinary.CloudinaryImage(
        f"Inst_project/{current_user.username}"
    ).build_url(
        width=250,
        height=250,
        crop="fill",
        version=r.get("version"),
        format=r.get("format"),
    )
    user_service = UserService(db)
    user = await user_service.update_avatar(current_user.username, src_url)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user

# ------------- ADMIN ROUTES -----------------------------------
@router.post("/{user_id}/ban", status_code=status.HTTP_200_OK)
async def ban_user(
    user_id: int,
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN])),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.ban_user(user_id)
    return {"message": "Success"}


@router.post("/{user_id}/unban", status_code=status.HTTP_200_OK)
async def ban_user(
    user_id: int,
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN])),  # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.unban_user(user_id)
    return {"message": "Success"}


@router.patch("/{user_id}/role", status_code=status.HTTP_200_OK)
async def change_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN])),   # TODO Check admin permission
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.change_role(user_id, role)
    return {"message": "Success"}

