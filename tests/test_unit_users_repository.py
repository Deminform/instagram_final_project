import pytest
from unittest.mock import AsyncMock, MagicMock
from starlette.datastructures import URL

from src.users.models import Role, User
from src.users.repository import UserRepository, RoleRepository
from src.users.schemas import UserCreate, UserUpdate, RoleEnum


@pytest.fixture
def session():
    return MagicMock()
@pytest.fixture
def mock_user():
    return User(
            id=1,
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

@pytest.fixture
def role():
    return Role(id=1, name=RoleEnum.ADMIN.value)

@pytest.mark.asyncio
async def test_create_user(session, mock_user):
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    user_repo = UserRepository(session)
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

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert created_user.first_name == mock_user.first_name
    assert created_user.last_name == mock_user.last_name
    assert created_user.phone == mock_user.phone
    assert created_user.username == mock_user.username
    assert created_user.email == mock_user.email
    assert created_user.avatar_url == mock_user.avatar_url
    assert created_user.role_id == mock_user.role_id
    assert created_user.password == mock_user.password


@pytest.mark.asyncio
async def test_get_user_by_email(session, mock_user):
    user_repo = UserRepository(session)
    user_email = mock_user.email

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute.return_value = mock_result
    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute

    result = await user_repo.get_user_by_email(user_email)
    assert result == mock_user
#
#
@pytest.mark.asyncio
async def test_get_user_by_username(session, mock_user):
    user_repo = UserRepository(session)
    username = mock_user.username

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute

    result = await user_repo.get_user_by_username(username)
    assert result == mock_user


@pytest.mark.asyncio
async def test_get_user_by_id(session, mock_user):
    user_repo = UserRepository(session)
    user_id = mock_user.id

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await user_repo.get_user_by_id(user_id)
    assert result == mock_user


@pytest.mark.asyncio
async def test_activate_user(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    await user_repo.activate_user(mock_user)
    assert mock_user.is_confirmed is True

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_update_user(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    update_data = UserUpdate(first_name="Jason",
                             last_name="Green",
                             phone="+380954442211",
                             username="ysullivan",
                             email="thomas15@yahoo.com")

    result = await user_repo.update_user(mock_user, update_data)

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)
    assert result == mock_user
    assert result.first_name == update_data.first_name
    assert result.last_name == update_data.last_name
    assert result.phone == update_data.phone
    assert result.username == update_data.username
    assert result.email == update_data.email


@pytest.mark.asyncio
async def test_update_avatar_url(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    username = mock_user.username
    url = URL("https://www.gravatar.com/avatar/5678")

    # Mock the repository method get_user_by_username
    user_repo.get_user_by_username = AsyncMock(return_value=mock_user)
    result = await user_repo.update_avatar_url(username, url)

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)
    assert result == mock_user
    assert mock_user.avatar_url == url


@pytest.mark.asyncio
async def test_get_user_posts_count(session, mock_user):
    user_repo = UserRepository(session)
    user_id = mock_user.id

    mock_result = MagicMock()
    mock_result.scalar.return_value = 5
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await user_repo.get_user_posts_count(user_id)
    assert result == 5


@pytest.mark.asyncio
async def test_ban_user(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    await user_repo.ban_user(mock_user)
    assert mock_user.is_banned is True

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_unban_user(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    mock_user.is_banned = True
    await user_repo.unban_user(mock_user)
    assert mock_user.is_banned is False

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_change_role(session, mock_user):
    user_repo = UserRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    user_role = Role(id=2, name="moderator")

    await user_repo.change_role(mock_user, user_role)
    assert mock_user.role_id == user_role.id

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_user)


# -----------------ROLE---------------------


@pytest.mark.asyncio
async def test_get_role_by_name(session, role):
    role_repo = RoleRepository(session)
    role_name = RoleEnum.ADMIN

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = role
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await role_repo.get_role_by_name(role_name)
    assert result == role
