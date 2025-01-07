from datetime import datetime
from typing import Sequence, Optional

from sqlalchemy import and_, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.datastructures import URL

from src.posts.models import Post
from src.users.models import Role, Token, User
from src.users.schemas import RoleEnum, UserCreate, UserUpdate, UserResponse



class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email address
        :param email: Email address to search for
        :type email: str
        :return: User object if found, otherwise None
        :rtype: User | None
        """
        query = select(User).options(selectinload(User.role)).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username
        :param username: Username to search for
        :type username: str
        :return: User object if found, otherwise None
        :rtype: User | None
        """
        query = (
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        user_create: UserCreate,
        user_role: Role,
        avatar: str,
        password_hashed: str,
    ) -> User:
        """
        Create a new user
        :param user_create: Data to create the user
        :type user_create: UserCreate
        :param user_role: Role assigned to the user
        :type user_role: Role
        :param avatar: URL for the user's avatar
        :type avatar: str
        :param password_hashed: Hashed password of the user
        :type password_hashed: str
        :return: Created user object
        :rtype: User
        """
        new_user = User(
            **user_create.model_dump(exclude_unset=True, exclude={"password"}),
            password=password_hashed,
            avatar_url=avatar,
            role_id=user_role.id,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def activate_user(self, user: User):
        """
        Activate a user account
        :param user: User to activate
        :type user: User
        """
        user.is_confirmed = True
        await self.session.commit()
        await self.session.refresh(user)

    async def get_user_by_id(self, user_id) -> User | None:
        """
        Retrieve a user by their ID
        :param user_id: ID of the user to search for
        :type user_id: int
        :return: User object if found, otherwise None
        :rtype: User | None
        """
        query = select(User).options(selectinload(User.role)).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user, body: UserUpdate) -> User:
        """
        Update user details
        :param user: User to update
        :type user: User
        :param body: Data for updating the user
        :type body: UserUpdate
        :return: Updated user object
        :rtype: User
        """
        updated_data = body.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(user, key, value)
        user.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_avatar_url(self, username: str, url: URL) -> User:
        """
        Update the avatar URL for a user
        :param username: Username of the user
        :type username: str
        :param url: New avatar URL
        :type url: URL
        :return: Updated user object
        :rtype: User
        """
        user = await self.get_user_by_username(username)
        user.avatar_url = url
        user.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def ban_user(self, user: User):
        """
        Ban a user
        :param user: User to ban
        :type user: User
        """
        user.is_banned = True
        await self.session.commit()
        await self.session.refresh(user)

    async def unban_user(self, user: User):
        """
        Unban a user
        :param user: User to unban
        :type user: User
        """
        user.is_banned = False
        await self.session.commit()
        await self.session.refresh(user)

    async def change_role(self, user: User, user_role: Role):
        """
        Change a user's role
        :param user: User whose role will be changed
        :type user: User
        :param user_role: New role to assign
        :type user_role: Role
        """
        user.role_id = user_role.id
        await self.session.commit()
        await self.session.refresh(user)

    async def get_user_posts_count(self, user_id):
        """
        Get the number of posts created by a user
        :param user_id: ID of the user
        :type user_id: int
        :return: Number of posts created by the user
        :rtype: int
        """
        query = select(func.count(Post.id)).where(Post.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def search_users(self, param: str, has_posts: bool, offset: int, limit: int) -> Sequence[User]:
        """
        Search for users based on criteria
        :param param: Search parameter (name or email)
        :type param: str
        :param has_posts: Filter by users with or without posts
        :type has_posts: bool
        :param offset: Offset for pagination
        :type offset: int
        :param limit: Limit for pagination
        :type limit: int
        :return: List of users matching the criteria
        :rtype: Sequence[User]
        """
        query = select(User, func.count(Post.id).label("posts_count")).outerjoin(Post).group_by(User.id)
        if param:
            query = query.filter(
                    or_(
                        User.first_name.ilike(f"%{param}%"),
                        User.last_name.ilike(f"%{param}%"),
                        User.email.ilike(f"%{param}%"),
                    )
                )

        if has_posts is True:
            query = query.having(func.count(Post.id) > 0)
        elif has_posts is False:
            query = query.having(func.count(Post.id) == 0)

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        rows = result.all()
        return [UserResponse.from_user(row.User, row.posts_count) for row in rows]

    async def create_admin_user(self, user_data: dict,
                                user_role: Role,
                                password_hashed: str,
                                avatar_url: Optional[str] = None,
       ) -> User:
        """
        Create a new admin user
        :param user_data: Data to create the admin user
        :type user_data: dict
        :param user_role: Role assigned to the admin
        :type user_role: Role
        :param password_hashed: Hashed password of the admin
        :type password_hashed: str
        :param avatar_url: URL for the admin's avatar (optional)
        :type avatar_url: Optional[str]
        :return: Created admin user object
        :rtype: User
        """
        new_admin = User(**user_data,
                         password=password_hashed,
                         avatar_url=avatar_url,
                         role_id=user_role.id,
                         is_confirmed=True,
                         )
        self.session.add(new_admin)
        await self.session.commit()
        await self.session.refresh(new_admin)
        return new_admin

    async def get_user_with_role(self, role_id: int):
        """
        Retrieve all users with a specific role
        :param role_id: ID of the role
        :type role_id: int
        :return: List of users with the specified role
        :rtype: list[User]
        """
        query = select(User).where(User.role_id == role_id)
        result = await self.session.execute(query)
        return result.scalars().all()



class RoleRepository:

    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        """
        Retrieve a role by its name
        :param name: Name of the role
        :type name: RoleEnum
        :return: Role object if found, otherwise None
        :rtype: Role | None
        """
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class TokenRepository:

    def __init__(self, session):
        self.session = session

    async def add_tokens(
        self, user_id: int, access_token: str, refresh_token: str, status: bool
    ):
        """
        Add access and refresh tokens for a user
        :param user_id: ID of the user
        :type user_id: int
        :param access_token: Access token
        :type access_token: str
        :param refresh_token: Refresh token
        :type refresh_token: str
        :param status: Activation status of the tokens
        :type status: bool
        """
        new_tokens = Token(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            is_active=status,
        )
        self.session.add(new_tokens)
        await self.session.commit()
        await self.session.refresh(new_tokens)

    async def get_active_token(self, user_id: int, token: str) -> Token | None:
        """
        Retrieve an active token for a user
        :param user_id: ID of the user
        :type user_id: int
        :param token: Access token to retrieve
        :type token: str
        :return: Token object if found and active, otherwise None
        :rtype: Token | None
        """
        query = select(Token).where(
            and_(Token.user_id == user_id),
            (Token.access_token == token),
            (Token.is_active.is_(True)),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_tokens(self, user_id: int) -> list:
        """
        Retrieve all tokens for a user
        :param user_id: ID of the user
        :type user_id: int
        :return: List of tokens for the user
        :rtype: list[Token]
        """
        query = select(Token).where(Token.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_tokens(self, expired_tokens: list):
        """
        Delete expired tokens from the database.
        :param expired_tokens: List of token IDs to delete
        :type expired_tokens: list
        """
        query = select(Token).where(Token.id.in_(expired_tokens))
        result = await self.session.execute(query)
        result = result.scalars().all()
        if result:
            for record in result:
                await self.session.delete(record)
                await self.session.commit()

    async def deactivate_user_tokens(self, user_id: int):
        """
        Deactivate all tokens for a specific user.
        :param user_id: ID of the user whose tokens should be deactivated
        :type user_id: int
        """
        query = select(Token).where(Token.user_id == user_id)
        result = await self.session.execute(query)
        result = result.scalars().all()
        if result:
            for record in result:
                record.is_active = False
                await self.session.commit()
                await self.session.refresh(record)
