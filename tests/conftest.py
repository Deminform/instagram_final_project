import asyncio
import io

import pytest
import pytest_asyncio
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.sql import text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from conf.config import Base, app_config
from database.db import get_db
from main import app
from src.posts.models import Post
from src.services.auth.auth_service import Hash, create_refresh_token, create_access_token
from src.users.models import User, Role, Token
from src.users.repository import UserRepository, TokenRepository

from src.scores.models import Score

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
            role_guest = Role(name='moderator')
            role_user = Role(name='user')
            role_admin = Role(name='admin')
            session.add(role_guest)
            session.add(role_user)
            session.add(role_admin)
            session.add(user)
            await session.commit()

        # Додавання тестового запису scores
            score = Score(post_id=1, user_id=user.id, score=4, id=1)
            session.add(score)
            score1 = Score(post_id=1, user_id=user.id, score=5, id=2)
            session.add(score1)

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


@pytest_asyncio.fixture(scope="module")
async def get_user():
    async with TestingSessionLocal() as session:
        return await UserRepository(session).get_user_by_email(test_user_dict['email'])


@pytest_asyncio.fixture(scope="module")
async def get_user_tokens():
    async with TestingSessionLocal() as session:
        access_token = create_access_token(data={"sub": test_user_dict['email']})
        refresh_token = create_refresh_token(data={"sub": test_user_dict['email']})
        await TokenRepository(session).add_tokens(1, access_token, refresh_token, True)
        return {"access_token": access_token, "refresh_token": refresh_token}

      
@pytest.fixture(scope="module")
def user_password(faker):
    password = faker.password()
    return password


@pytest_asyncio.fixture(scope="module")
async def test_user_auth(init_models_wrap, user_password, faker):
    async with TestingSessionLocal() as session:
        hashed_password = Hash().get_password_hash(user_password)
        user = User(
                first_name="Melanie",
                last_name="Grant",
                phone="+380993332233",
                username="sheena09",
                email="kimberly00@yahoo.com",
                avatar_url="https://www.gravatar.com/avatar/1234",
                role_id=2,
                password=hashed_password,
                is_banned=False,
                is_confirmed=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

@pytest_asyncio.fixture(scope="function")
async def auth_header(test_user_auth):
    async with TestingSessionLocal() as session:
        access_token = create_access_token(data={"sub": test_user_auth.email})
        refresh_token = create_refresh_token(data={"sub": test_user_auth.email})
        token = Token(
            user_id=test_user_auth.id,
            access_token=access_token,
            refresh_token=refresh_token,
            is_active=True
        )
        session.add(token)
        await session.commit()
        await session.refresh(token)
        return {"access_token": access_token, "refresh_token": refresh_token}


@pytest_asyncio.fixture(autouse=True)
async def cleanup_user_tokens(request, test_user_auth):

    async with TestingSessionLocal() as session:
        query = text("DELETE FROM tokens WHERE user_id = :user_id")
        await session.execute(query, {"user_id": test_user_auth.id})
        await session.commit()


@pytest_asyncio.fixture(scope="module")
async def get_test_user_auth():
    async def _get_test_user_auth(user_id: int):
        async with TestingSessionLocal() as session:
            return await UserRepository(session).get_user_by_id(user_id)
    return _get_test_user_auth


@pytest_asyncio.fixture(scope="function")
async def create_post(test_user_auth):
    async with TestingSessionLocal() as session:
        post = Post(description="My post description",
                    user_id=test_user_auth.id,
                    original_image_url="https://res.cloudinary.com/example/my_image.jpg",
                    image_url="https://res.cloudinary.com/example/my_edited_image.jpg",
                    )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post


@pytest_asyncio.fixture(scope="module")
async def get_test_user_token():
    async def _get_test_user_token(user_id: int):
        async with TestingSessionLocal() as session:
            return await TokenRepository(session).get_user_tokens(user_id)
    return _get_test_user_token

