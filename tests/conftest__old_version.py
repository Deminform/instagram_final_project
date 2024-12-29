import asyncio
import io

import pytest
import pytest_asyncio
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from conf.config import Base, app_config
from database.db import get_db
from main import app
from src.services.auth.auth_service import Hash, create_refresh_token, create_access_token, TokenRepository
from src.users.models import User, Role
from src.users.repository import UserRepository, TokenRepository

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user_dict = {
        "first_name": "Steve",
        "last_name": "Stevenson",
        "phone": "1234567890",
        "username": "SteveStevenson",
        "email": "steve@example.com",
        "avatar_url": "https://www.gravatar.com/avatar/1234",
        "role_id": 3,
        "password":"000000",
        "is_banned":False,
        "is_confirmed":True,
}

@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user_dict['password'])
            user = User(
                first_name=test_user_dict["first_name"],
                last_name=test_user_dict["last_name"],
                phone=test_user_dict["phone"],
                username=test_user_dict["username"],
                email=test_user_dict["email"],
                avatar_url=test_user_dict["avatar_url"],
                role_id=3,
                password=hash_password,
                is_banned=False,
                is_confirmed=True,
            )
            role_guest = Role(name='guest')
            role_user = Role(name='user')
            role_admin = Role(name='admin')
            session.add(role_guest)
            session.add(role_user)
            session.add(role_admin)
            session.add(user)
            await session.commit()
    asyncio.run(init_models())

@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            await session.rollback()
            raise err
        finally:
            await session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest_asyncio.fixture()
async def file_fixture():
    img = Image.new('RGB', (100, 100), color=(0, 0, 0))
    fake_file = io.BytesIO()
    img.save(fake_file, format='JPEG')
    fake_file.seek(0)
    fake_file.name = "test_image.jpg"
    return fake_file


@pytest_asyncio.fixture()
async def get_user():
    async with TestingSessionLocal() as session:
        return await UserRepository(session).get_user_by_email(test_user_dict['email'])


@pytest_asyncio.fixture()
async def get_user_tokens():
    async with TestingSessionLocal() as session:
        access_token = create_access_token(data={"sub": test_user_dict['email']})
        refresh_token = create_refresh_token(data={"sub": test_user_dict['email']})
        await TokenRepository(session).add_tokens(1, access_token, refresh_token, True)
        return {"access_token": access_token, "refresh_token": refresh_token}

