from datetime import datetime
from typing import Sequence

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
        query = select(User).options(selectinload(User.role)).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
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
        user.is_confirmed = True
        await self.session.commit()
        await self.session.refresh(user)

    async def get_user_by_id(self, user_id) -> User | None:
        query = select(User).options(selectinload(User.role)).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user, body: UserUpdate) -> User:
        updated_data = body.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(user, key, value)
        user.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_avatar_url(self, username: str, url: URL) -> User:
        user = await self.get_user_by_username(username)
        user.avatar_url = url
        user.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def ban_user(self, user: User):
        user.is_banned = True
        await self.session.commit()
        await self.session.refresh(user)

    async def unban_user(self, user: User):
        user.is_banned = False
        await self.session.commit()
        await self.session.refresh(user)

    async def change_role(self, user: User, user_role: Role):
        user.role_id = user_role.id
        await self.session.commit()
        await self.session.refresh(user)

    async def get_user_posts_count(self, user_id):
        query = select(func.count(Post.id)).where(Post.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def search_users(self, param: str, has_posts: bool, offset: int, limit: int) -> Sequence[User]:
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


class RoleRepository:

    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class TokenRepository:

    def __init__(self, session):
        self.session = session

    async def add_tokens(
        self, user_id: int, access_token: str, refresh_token: str, status: bool
    ):
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
        query = select(Token).where(
            and_(Token.user_id == user_id),
            (Token.access_token == token),
            (Token.is_active.is_(True)),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_tokens(self, user_id: int) -> list:
        query = select(Token).where(Token.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_tokens(self, expired_tokens: list):
        query = select(Token).where(Token.id.in_(expired_tokens))
        result = await self.session.execute(query)
        result = result.scalars().all()
        if result:
            for record in result:
                await self.session.delete(record)
                await self.session.commit()

    async def deactivate_user_tokens(self, user_id: int):
        query = select(Token).where(Token.user_id == user_id)
        result = await self.session.execute(query)
        result = result.scalars().all()
        if result:
            for record in result:
                record.is_active = False
                await self.session.commit()
                await self.session.refresh(record)
