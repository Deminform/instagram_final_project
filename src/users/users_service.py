from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from starlette.datastructures import URL

from conf.messages import USER_NOT_FOUND
from src.services.auth.auth_service import Hash
from src.users.models import User
from src.users.repos import UserRepository, RoleRepository, TokenRepository
from src.users.schema import UserCreate, RoleEnum, UserUpdate

def _handle_integrity_error(e: IntegrityError):
    if "unique" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data already exist.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity error.",
        )

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.token_repository = TokenRepository(db)

    async def create_user(self, user_create: UserCreate) -> User:
        avatar = None
        user_role = await self.role_repository.get_role_by_name(RoleEnum.USER)
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        password_hashed = Hash().get_password_hash(user_create.password)

        return await self.user_repository.create_user(user_create, user_role, avatar, password_hashed)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_username(self, username) -> User | None:
        return await self.user_repository.get_user_by_username(username)

    async def activate_user(self, user):
        return await self.user_repository.activate_user(user)

    async def update_user(self, user_id: int, body: UserUpdate) -> User | None:
        user = await self.user_repository.get_user_by_id(user_id)
        try:
            if user:
                return await self.user_repository.update_user(user, body)
        except IntegrityError as e:
            _handle_integrity_error(e)

    async def update_avatar(self, username: str, url: URL):
        return await self.user_repository.update_avatar_url(username, url)

    async def ban_user(self, user_id: int):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=USER_NOT_FOUND)
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already banned")
        return await self.user_repository.ban_user(user)


    async def unban_user(self, user_id: int):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=USER_NOT_FOUND)
        if not user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already not banned")
        return await self.user_repository.unban_user(user)

    async def change_role(self, user_id: int, role: str):
        user = await self.user_repository.get_user_by_id(user_id)
        user_role = await self.role_repository.get_role_by_name(RoleEnum(role))
        if not user:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=USER_NOT_FOUND)
        return await self.user_repository.change_role(user, user_role)

    async def add_tokens_db(self, user_id: int, access_token: str, refresh_token: str, status: bool):
        return await self.token_repository.add_tokens(user_id, access_token, refresh_token, status)









