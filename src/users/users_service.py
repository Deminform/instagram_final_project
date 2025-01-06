from typing import Sequence

from fastapi import HTTPException, status, UploadFile
from libgravatar import Gravatar
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from conf.messages import (
    USER_NOT_FOUND,
    DATA_INTEGRITY_ERROR,
    DATA_NOT_UNIQUE,
    ALREADY_BANNED,
    NOT_BANNED,
)
from src.services.auth.auth_service import Hash
from src.users.models import User
from src.users.repository import RoleRepository, TokenRepository, UserRepository
from src.users.schemas import RoleEnum, UserCreate, UserUpdate, UserResponse
from src.services.cloudinary_service import CloudinaryService


def _handle_integrity_error(e: IntegrityError):
    if "unique" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DATA_NOT_UNIQUE,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DATA_INTEGRITY_ERROR,
        )


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.token_repository = TokenRepository(db)
        self.cloudinary_service = CloudinaryService()

    async def create_user(self, user_create: UserCreate) -> User:
        avatar = None
        user_role = await self.role_repository.get_role_by_name(RoleEnum.USER)
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        password_hashed = Hash().get_password_hash(user_create.password)

        return await self.user_repository.create_user(
            user_create, user_role, avatar, password_hashed
        )

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        posts_count = await self.user_repository.get_user_posts_count(user.id)
        return UserResponse.from_user(user, posts_count)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str) -> UserResponse | None:
        user = await self.user_repository.get_user_by_username(username)
        if user:
            posts_count = await self.user_repository.get_user_posts_count(user.id)
            return UserResponse.from_user(user, posts_count)

    async def activate_user(self, user: User):
        return await self.user_repository.activate_user(user)

    async def update_user(self, user_id: int, body: UserUpdate) -> UserResponse | None:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        try:
            update_user = await self.user_repository.update_user(user, body)
            posts_count = await self.user_repository.get_user_posts_count(user.id)
            return UserResponse.from_user(update_user, posts_count)
        except IntegrityError as e:
            _handle_integrity_error(e)

    async def update_avatar(self, username: str, avatar_file: UploadFile):
        avatar_url = await self.cloudinary_service.get_avatar_url(avatar_file, username)
        return await self.user_repository.update_avatar_url(username, avatar_url)

    # -------ADMIN ENDPOINTS-------

    async def ensure_admin_exists(self):
        user_role = await self.role_repository.get_role_by_name(RoleEnum.ADMIN)
        admin_user = await self.user_repository.get_user_with_role(user_role)
        if not admin_user:
            avatar = None
            user_create = UserCreate(
                first_name="admin",
                last_name="admin",
                phone="+1234567890",
                username="admin",
                email="admin@example.com",
                password="secure-password",
            )
            try:
                g = Gravatar(user_create.email)
                avatar = g.get_image()
            except Exception as e:
                print(e)
            password_hashed = Hash().get_password_hash(user_create.password)

            return await self.user_repository.create_user(user_create, user_role, avatar, password_hashed
            )
        else:
            print("Admin user already exists.")


    async def ban_user(self, user_id: int):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ALREADY_BANNED
            )
        return await self.user_repository.ban_user(user)

    async def unban_user(self, user_id: int):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        if not user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NOT_BANNED,
            )
        return await self.user_repository.unban_user(user)

    async def change_role(self, user_id: int, role: str):
        user = await self.user_repository.get_user_by_id(user_id)
        user_role = await self.role_repository.get_role_by_name(RoleEnum(role))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        return await self.user_repository.change_role(user, user_role)

    async def search_users(self, param: str, has_posts: bool, offset: int, limit: int) -> Sequence[User] | None:
        return await self.user_repository.search_users(param, has_posts, offset, limit)


