from typing import Sequence
from dotenv import load_dotenv
import os

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

load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
        """
        Create a new user in the system.
        :param user_create: The data required to create a new user.
        :type user_create: UserCreate
        :return: The created user object.
        :rtype: User
        """
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
        """
        Retrieve user information by ID.
        :param user_id: The ID of the user to retrieve.
        :type user_id: int
        :return: User information response model if the user is found, otherwise None.
        :rtype: UserResponse | None
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        posts_count = await self.user_repository.get_user_posts_count(user.id)
        return UserResponse.from_user(user, posts_count)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.
        :param email: The email address of the user to search for.
        :type email: str
        :return: User object if found, otherwise None.
        :rtype: User | None
        """
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str) -> UserResponse | None:
        """
        Retrieve user information by their username.
        :param username: The username of the user to retrieve.
        :type username: str
        :return: User information response model if the user is found, otherwise None.
        :rtype: UserResponse | None
        """
        user = await self.user_repository.get_user_by_username(username)
        if user:
            posts_count = await self.user_repository.get_user_posts_count(user.id)
            return UserResponse.from_user(user, posts_count)

    async def activate_user(self, user: User):
        """
        Activate a user account.
        :param user: The user to activate.
        :type user: User
        :return: The updated user object.
        :rtype: User
        """
        return await self.user_repository.activate_user(user)

    async def update_user(self, user_id: int, body: UserUpdate) -> UserResponse | None:
        """
        Update the information of a user by their ID.
        :param user_id: The ID of the user to update.
        :type user_id: int
        :param body: The new data to update the user with.
        :type body: UserUpdate
        :return: The updated user information if successful, otherwise None.
        :rtype: UserResponse | None
        """
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
        """
        Update the avatar of a user.
        :param username: The username of the user whose avatar to update.
        :type username: str
        :param avatar_file: The new avatar file to upload.
        :type avatar_file: UploadFile
        :return: The updated user object with the new avatar URL.
        :rtype: User
        """
        avatar_url = await self.cloudinary_service.get_avatar_url(avatar_file, username)
        return await self.user_repository.update_avatar_url(username, avatar_url)

    # -------ADMIN ENDPOINTS-------

    async def ensure_admin_exists(self):
        """
        Ensure that an admin user exists in the system. If not, create one.
        :return: None
        :rtype: None
        """
        user_role = await self.role_repository.get_role_by_name(RoleEnum.ADMIN)
        admin_user = await self.user_repository.get_user_with_role(user_role.id)

        if not admin_user:
            avatar = None
            admin_create = {
                "first_name": "admin",
                "last_name": "admin",
                "phone": "+1234567890",
                "username": "admin",
                "email": ADMIN_EMAIL,

            }
            try:
                g = Gravatar(admin_create["email"])
                avatar = g.get_image()
            except Exception as e:
                print(e)
            password = ADMIN_PASSWORD
            password_hashed = Hash().get_password_hash(password)

            try:
                await self.user_repository.create_admin_user(admin_create, user_role, password_hashed, avatar)
                print("Admin user created successfully.")
            except IntegrityError as e:
                raise RuntimeError(e)
        else:
            print("Admin user already exists.")


    async def ban_user(self, user_id: int):
        """
        Ban a user by their ID.
        :param user_id: The ID of the user to ban.
        :type user_id: int
        :return: The banned user object.
        :rtype: User
        """
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
        """
        Unban a user by their ID.
        :param user_id: The ID of the user to unban.
        :type user_id: int
        :return: The unbanned user object.
        :rtype: User
        """
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
        """
        Change the role of a user by their ID.
        :param user_id: The ID of the user whose role to change.
        :type user_id: int
        :param role: The new role to assign to the user.
        :type role: str
        :return: The updated user object with the new role.
        :rtype: User
        """
        user = await self.user_repository.get_user_by_id(user_id)
        user_role = await self.role_repository.get_role_by_name(RoleEnum(role))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )
        return await self.user_repository.change_role(user, user_role)

    async def search_users(self, param: str, has_posts: bool, offset: int, limit: int) -> Sequence[User] | None:
        """
        Search for users based on various parameters.
        :param param: Search term for first name, last name, or email.
        :type param: str
        :param has_posts: Whether to filter users who have posts.
        :type has_posts: bool
        :param offset: The offset for pagination.
        :type offset: int
        :param limit: The number of users to return (pagination).
        :type limit: int
        :return: A list of users matching the search criteria.
        :rtype: Sequence[User] | None
        """
        return await self.user_repository.search_users(param, has_posts, offset, limit)


