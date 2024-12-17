from sqlalchemy import select
from libgravatar import Gravatar

from src.auth.models import User, Role
from src.auth.pass_utils import get_password_hash
from src.auth.schema import UserCreate, RoleEnum


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_create: UserCreate) -> User:
        avatar = None
        user_role = await RoleRepository(self.session).get_role_by_name(RoleEnum.USER)
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        password_hashed = get_password_hash(user_create.password)
        new_user = User(
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            phone=user_create.phone,
            username=user_create.username,
            email=user_create.email,
            password=password_hashed,
            avatar_url=avatar,
            role_id=user_role.id,
            is_confirmed=False,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def activate_user(self, user: User):
        user.is_confirmed = True
        await self.session.commit()
        await self.session.refresh(user)


class RoleRepository:

    def __init__(self, session):
        self.session = session

    async def get_role_by_name(self, name: RoleEnum):
        query = select(Role).where(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()