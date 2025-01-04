import pytest

from unittest.mock import AsyncMock, MagicMock
from starlette.datastructures import URL

from src.users.models import Role, User, Token
from src.users.repository import UserRepository, RoleRepository, TokenRepository
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
            created_at="2024-12-30T20:03:22.518226",
            updated_at="2024-12-30T20:03:22.518226",
            is_banned=False,
            is_confirmed=False
    )

@pytest.fixture
def mock_user_additional():
    return User(
            id=1,
            first_name="Melinda",
            last_name="Mann",
            phone="+380991122334",
            username="lisa83",
            email="barbara42@gmail.com",
            avatar_url="https://www.gravatar.com/avatar/4321",
            role_id=3,
            password="hashed_password",
            created_at="2024-12-30T20:03:22.518226",
            updated_at="2024-12-30T20:03:22.518226",
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


@pytest.mark.asyncio
async def test_search_users(session, mock_user, mock_user_additional):
    param = "Mel"
    has_posts = True
    offset = 0
    limit = 10
    user_repo = UserRepository(session)

    mock_result = MagicMock()
    mock_result.all.return_value = [
        MagicMock(User=mock_user, posts_count=5), MagicMock(User=mock_user_additional, posts_count=10)
    ]
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await user_repo.search_users(param, has_posts, offset, limit)
    assert len(result) == 2
    assert result[0].first_name == "Melanie"
    assert result[0].post_count == 5
    assert result[1].first_name == "Melinda"
    assert result[1].post_count == 10




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


# -----------------TOKENS---------------------

@pytest.fixture
def mock_token():
    token1 = Token(
        user_id=1,
        access_token="erewfsdferewre",
        refresh_token="vdv6d7s67ds67",
        is_active=True,
    )
    token2 = Token(
        user_id=1,
        access_token="kgjfjkhgjhgjdg",
        refresh_token="nvfdjvhfduv6f",
        is_active=True,
    )
    return [token1, token2]
@pytest.mark.asyncio
async def test_add_tokens(session, mock_user):
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    token_repo = TokenRepository(session)
    access_token = "erewfsdferewre"
    refresh_token = "vdv6d7s67ds67"
    status = True

    await token_repo.add_tokens(mock_user.id, access_token, refresh_token, status)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    added_token = session.add.call_args[0][0]
    assert added_token.user_id == mock_user.id
    assert added_token.access_token == access_token
    assert added_token.refresh_token == refresh_token
    assert added_token.is_active == status


@pytest.mark.asyncio
async def test_get_active_token(session, mock_user, mock_token):
    token_repo = TokenRepository(session)
    user_id = mock_user.id
    token = mock_token[0].access_token

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_token[0]
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await token_repo.get_active_token(user_id, token)
    assert result == mock_token[0]


@pytest.mark.asyncio
async def test_get_user_tokens(session, mock_user, mock_token):
    token_repo = TokenRepository(session)
    user_id = mock_user.id

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_token
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    result = await token_repo.get_user_tokens(user_id)
    assert result == mock_token


@pytest.mark.asyncio
async def test_deactivate_user_tokens(session, mock_user, mock_token):
    token_repo = TokenRepository(session)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    user_id = mock_user.id

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_token
    session.execute.return_value = mock_result

    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    await token_repo.deactivate_user_tokens(user_id)
    for token in mock_token:
        assert token.is_active is False


@pytest.mark.asyncio
async def test_delete_tokens(session, mock_token):
    token_repo = TokenRepository(session)
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    expired_tokens_ids = [token.id for token in mock_token]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_token
    session.execute.return_value = mock_result
    async def mock_execute(query):
        return mock_result

    session.execute = mock_execute
    await token_repo.delete_tokens(expired_tokens_ids)

    for token in mock_token:
        session.delete.assert_any_call(token)
        session.commit.assert_any_call()
