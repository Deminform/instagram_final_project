import io
from io import BytesIO
from PIL import Image

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from main import app
from src.users.models import User, Role
from src.services.auth.auth_service import Hash, create_access_token, create_refresh_token
from conf.config import Base, app_config
from database.db import get_db
from src.users.schemas import RoleEnum
from src.users.repository import TokenRepository


# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger("test_logger")


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

engine = create_async_engine(app_config.TEST_DB_URL, echo=False)
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
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def override_get_db():
    async def _get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def user_password(faker):
    password = faker.password()
    return password


@pytest_asyncio.fixture(scope="function")
async def file_fixture():
    file_content = b"This is a test image content"
    fake_file = BytesIO(file_content)
    fake_file.name = "test_image.jpg"
    return fake_file


@pytest_asyncio.fixture(scope="function")
async def user_role(db_session):
    role_1 = Role(id=1, name=RoleEnum.USER.value)
    role_2 = Role(id=2, name=RoleEnum.MODER.value)
    role_3 = Role(id=3, name=RoleEnum.ADMIN.value)

    db_session.add(role_1)
    db_session.add(role_2)
    db_session.add(role_3)
    await db_session.commit()
    await db_session.refresh(role_1)
    await db_session.refresh(role_2)
    await db_session.refresh(role_3)



@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, user_password, user_role):
    hashed_password = Hash().get_password_hash(user_password)

    user = User(
        first_name=test_user_dict["email"],
        last_name=test_user_dict["last_name"],
        phone=test_user_dict["phone"],
        username=test_user_dict["username"],
        email=test_user_dict["email"],
        avatar_url=test_user_dict["avatar_url"],
        role_id=3,
        password=hashed_password,
        is_banned=False,
        is_confirmed=True)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def get_user_tokens(db_session):
        access_token = create_access_token(data={"sub": test_user_dict['email']})
        refresh_token = create_refresh_token(data={"sub": test_user_dict['email']})
        await TokenRepository(db_session).add_tokens(1, access_token, refresh_token, True)
        return {"access_token": access_token, "refresh_token": refresh_token}


@pytest_asyncio.fixture(scope="function")
async def file_fixture():
    img = Image.new('RGB', (100, 100), color=(0, 0, 0))
    fake_file = io.BytesIO()
    img.save(fake_file, format='JPEG')
    fake_file.seek(0)
    fake_file.name = "test_image.jpg"
    return fake_file