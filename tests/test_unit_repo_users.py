import pytest
from unittest.mock import AsyncMock, MagicMock

from src.users.models import Role
from src.users.repos import UserRepository, User
from src.users.schema import UserCreate


@pytest.fixture
def mock_user():
    mock_user = User(
            first_name="Melanie",
            last_name="Grant",
            phone="+380993332233",
            username="sheena09",
            email="kimberly00@yahoo.com",
            avatar_url="https://www.gravatar.com/avatar/1234",
            role_id=3,
            password="hashed_password",
            created_at="",
            updated_at="",
            is_banned=False,
            is_confirmed=False
    )
    return mock_user


@pytest.mark.asyncio
async def test_create_user(mock_user):
    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    user_repo = UserRepository(mock_session)
    new_user = UserCreate(first_name="Melanie",
                          last_name="Grant",
                          phone="+380993332233",
                          username="sheena09",
                          email="kimberly00@yahoo.com",
                          password="password123",)
    user_role = Role(id=3, name="User")
    avatar = "https://www.gravatar.com/avatar/1234"
    password_hashed = "hashed_password"
    created_user = await user_repo.create_user(new_user, user_role, avatar, password_hashed)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert created_user.first_name == mock_user.first_name
    assert created_user.last_name == mock_user.last_name
    assert created_user.phone == mock_user.phone
    assert created_user.username == mock_user.username
    assert created_user.email == mock_user.email
    assert created_user.avatar_url == mock_user.avatar_url
    assert created_user.role_id == mock_user.role_id
    assert created_user.password == mock_user.password


@pytest.mark.asyncio
async def test_get_user_by_email(mock_user):
    mock_session = MagicMock()
    mocked_result = MagicMock()
    mocked_result.scalar_one_or_none.return_value = mock_user
    async def mock_execute(query):
        return mocked_result

    mock_session.execute = mock_execute

    user_repo = UserRepository(mock_session)
    user_email = "kimberly00@yahoo.com"
    user = await user_repo.get_user_by_email(user_email)
    assert user == mock_user


@pytest.mark.asyncio
async def test_get_user_by_username(mock_user):
    mock_session = MagicMock()
    mocked_result = MagicMock()
    mocked_result.scalar_one_or_none.return_value = mock_user
    async def mock_execute(query):
        return mocked_result

    mock_session.execute = mock_execute

    user_repo = UserRepository(mock_session)
    username = "sheena09"
    user = await user_repo.get_user_by_username(username)
    assert user == mock_user


@pytest.mark.asyncio
async def test_get_user_by_id(mock_user):
    mock_session = MagicMock()
    mocked_result = MagicMock()
    mocked_result.scalar_one_or_none.return_value = mock_user
    async def mock_execute(query):
        return mocked_result

    mock_session.execute = mock_execute

    user_repo = UserRepository(mock_session)
    user_id = "sdsd"
    user = await user_repo.get_user_by_id(user_id)
    assert user == mock_user
