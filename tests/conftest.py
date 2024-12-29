import asyncio
from datetime import datetime
import logging

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from main import app
from src.users.models import User, Role, Token
from src.services.auth.auth_service import Hash, create_access_token, create_refresh_token
from conf.config import Base, app_config
from database.db import get_db
from src.users.schemas import RoleEnum

TEST_DB_URL = app_config.DATABASE_TEST_URL
engine = create_async_engine(TEST_DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)

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


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop to be used in tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def override_get_db():
    async def _get_db():
        logging.info("Opening DB session")
        async with AsyncSessionLocal() as session:
            yield session
        logging.info("Closing DB session")

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def user_password(faker):
    return faker.password()


@pytest_asyncio.fixture(scope="function")
async def user_role(db_session) -> Role:
    role = Role(
        id=1,
        name=RoleEnum.USER.value,
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, faker, user_password, user_role):
    hashed_password = Hash().get_password_hash(user_password)
    user = User(
        first_name=test_user_dict["email"],
        last_name=test_user_dict["last_name"],
        phone=test_user_dict["phone"],
        username=test_user_dict["username"],
        email=test_user_dict["email"],
        avatar_url=test_user_dict["avatar_url"],
        role_id=1,
        password=hashed_password,
        is_banned=False,
        is_confirmed=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def auth_header(db_session, test_user: User):
    access_token = create_access_token({"sub": test_user.email})
    refresh_token = create_refresh_token({"sub": test_user.email})
    token = Token(
        user_id=1,
        access_token=access_token,
        refresh_token=refresh_token,
        is_active=True
    )
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)

    headers = {
        "Authorization": f"Bearer {access_token}"
        # "X-Refresh-Token": refresh_token
    }
    return headers

# @pytest_asyncio.fixture(scope="function")
# async def get_user_tokens(db_session):
#         access_token = create_access_token(data={"sub": test_user_dict['email']})
#         refresh_token = create_refresh_token(data={"sub": test_user_dict['email']})
#         await TokenRepository(db_session).add_tokens(1, access_token, refresh_token, True)
#         return {"access_token": access_token, "refresh_token": refresh_token}


