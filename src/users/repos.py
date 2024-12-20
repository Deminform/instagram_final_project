from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User, Role
from src.users.schema import UserCreate, RoleEnum


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_create: UserCreate, user_role: Role, avatar: str, password_hashed: str) -> User:
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

    async def get_user(self, id) -> User | None:
        query = select(User).where(User.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, id):
        pass

    async def ban_user(self, id):
        pass

    async def unban_user(self, id):
        pass


class RoleRepository:

    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()