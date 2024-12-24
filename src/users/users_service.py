from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth.auth_service import Hash
from src.users.models import User
from src.users.repos import UserRepository, RoleRepository
from src.users.schema import UserCreate, RoleEnum


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

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

    async def get_user_by_email(self, email):
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_username(self, username):
        return await self.user_repository.get_user_by_username(username)

    async def activate_user(self, user):
        return await self.user_repository.activate_user(user)



def get_current_user_info():
    pass


def update_user():
    pass


def ban_user():
    pass

def unban_user():
    pass