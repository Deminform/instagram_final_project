import asyncio
from datetime import datetime
import logging

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from main import app
from src.users.models import User, Role
from src.services.auth.auth_service import Hash
from conf.config import Base, app_config
from database.db import get_db
from src.users.schemas import RoleEnum


TEST_DB_URL = "GBPLTW"
print("DATABASE_TEST_URL:", TEST_DB_URL)
engine = create_async_engine(TEST_DB_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)


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
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        phone=faker.phone_number()[:15],
        username=faker.user_name(),
        email=faker.email(),
        avatar_url="https://www.gravatar.com/avatar/1234",
        role_id=user_role.id,
        password=hashed_password,
        created_at=datetime.now,
        updated_at=datetime.now,
        is_banned=False,
        is_confirmed=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

