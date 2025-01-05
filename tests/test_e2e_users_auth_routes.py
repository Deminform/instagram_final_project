import asyncio

import pytest
from unittest.mock import patch

import pytest_asyncio
from fastapi import BackgroundTasks

from conf.messages import EMAIL_CONFIRMED
from src.services.auth.auth_service import create_verification_token, Hash
from src.users.models import Role, User
from src.users.repository import UserRepository
from tests.conftest import TestingSessionLocal


# TODO Refresh


def test_user_registration(client, faker):
    with patch.object(BackgroundTasks, "add_task") as mock_add_task:
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "phone": "+380661233322",
            "username": faker.user_name(),
            "email": faker.email(),
            "password": faker.password(),
        }

        response = client.post('api/auth/signup', json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data['first_name'] == payload['first_name']
        assert data['last_name'] == payload['last_name']
        assert data['phone'] == payload['phone']
        assert data['username'] == payload['username']
        assert data['email'] == payload['email']
        assert data.get("password") is None
        assert data["id"] is not None
        assert data["role_name"] == "user"
        assert data["avatar_url"] is not None
        assert data["is_confirmed"] == False
        assert data["is_banned"] == False
        mock_add_task.assert_called_once()


def test_verify_email(client, faker):
    with patch.object(BackgroundTasks, "add_task") as mock_add_task:
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "phone": "+380661233322",
            "username": faker.user_name(),
            "email": faker.email(),
            "password": faker.password(),
        }
        response = client.post('api/auth/signup', json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        email = data['email']
        mock_add_task.assert_called_once()

    token = create_verification_token(email)
    response = client.get(f'api/auth/verify-email?token={token}')
    assert response.status_code == 200, response.text
    assert response.json() == {"message": EMAIL_CONFIRMED}

    async def get_user(email):
        async with TestingSessionLocal() as session:
            return await UserRepository(session).get_user_by_email(email)

    user = asyncio.run(get_user(email))
    assert user.is_confirmed


def test_user_login(client, test_user_auth, user_password, create_post):
    payload = {
        "username": test_user_auth.email,
        "password": user_password

    }
    response = client.post('api/auth/login', data=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token(client, auth_header):
    response = client.post(f"api/auth/refresh?refresh_token={auth_header['refresh_token']}")
    assert response.status_code == 200, response.text
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


def test_logout(client, test_user_auth, auth_header, get_test_user_token):

    response = client.get('api/auth/logout', headers={"Authorization": f"Bearer {auth_header['access_token']}"})
    assert response.status_code == 200, response.text
    print(f"lalal {auth_header["access_token"]}")
    tokens = asyncio.run(get_test_user_token(test_user_auth.id))
    for token in tokens:
        assert token.is_active is False


def test_get_user_by_id(client, test_user_auth, auth_header, get_test_user_token):
    tokens = asyncio.run(get_test_user_token(test_user_auth.id))
    for token in tokens:
        print(f"Test Logout: {token.is_active}")
    response = client.get(f"/api/users/{test_user_auth.id}", headers={"Authorization": f"Bearer {auth_header['access_token']}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['first_name'] == test_user_auth.first_name
    assert data['last_name'] == test_user_auth.last_name
    assert data['phone'] == test_user_auth.phone
    assert data['username'] == test_user_auth.username
    assert data['email'] == test_user_auth.email
    assert data.get("password") is None
    assert data["id"] == test_user_auth.id
    assert data["role_name"] == 'user'
    assert data["post_count"] == 1
    assert data["avatar_url"] is not None
    assert data["is_confirmed"] is True
    assert data["is_banned"] is False
    tokens = asyncio.run(get_test_user_token(test_user_auth.id))
    for token in tokens:
        print(f"Test Logout: {token.is_active}")


def test_get_user_username(client, test_user_auth, auth_header):
    response = client.get(f"/api/users/{test_user_auth.username}/profile",
                          headers={"Authorization": f"Bearer {auth_header['access_token']}"})
    assert response.status_code == 200, response.text
    data = response.json()

    assert data['first_name'] == test_user_auth.first_name
    assert data['last_name'] == test_user_auth.last_name
    assert data['phone'] == test_user_auth.phone
    assert data['username'] == test_user_auth.username
    assert data['email'] == test_user_auth.email
    assert data.get("password") is None
    assert data["id"] == test_user_auth.id
    assert data["role_name"] == 'user'
    assert data["post_count"] == 1
    assert data["avatar_url"] is not None
    assert data["is_confirmed"] is True
    assert data["is_banned"] is False


def test_user_update_avatar(client, auth_header, file_fixture, test_user_auth, get_test_user_auth):
    response = client.patch('api/users/avatar', headers={"Authorization": f"Bearer {auth_header['access_token']}"},
                            files={"file": (file_fixture.name, file_fixture, "file/jpeg")},)
    assert response.status_code == 200, response.text
    data = response.json()
    user = asyncio.run(get_test_user_auth(test_user_auth.id))
    assert data['avatar_url'] == user.avatar_url


def test_user_update_info(client, faker, auth_header, test_user_auth):
    payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "phone": "+380671112233",
        "username": faker.user_name(),
        "email": faker.email(),
    }

    response = client.patch('api/users/info', headers={"Authorization": f"Bearer {auth_header['access_token']}"},
                            json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['first_name'] == payload['first_name']
    assert data['first_name'] != test_user_auth.first_name
    assert data['last_name'] == payload['last_name']
    assert data['phone'] == payload['phone']
    assert data['username'] == payload['username']
    assert data['email'] == payload['email']
    print(f"Test Logout Token: {auth_header['access_token']}")


# -----------------ADMIN---------------------

def test_ban_user(client, test_user_auth, get_user_tokens, get_test_user_auth):

    response = client.post(f"/api/admin/user/{test_user_auth.id}/ban",
                           headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"})
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Success"}

    user = asyncio.run(get_test_user_auth(test_user_auth.id))
    assert user.is_banned is True


def test_unban_user(client, test_user_auth, get_user_tokens, get_test_user_auth):
    response = client.post(f"/api/admin/user/{test_user_auth.id}/unban",
                           headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"})
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Success"}

    user = asyncio.run(get_test_user_auth(test_user_auth.id))
    assert user.is_banned is False


def test_change_user_role(client, test_user_auth, get_user_tokens, get_test_user_auth):
    role = "moderator"
    response = client.patch(f"/api/admin/user/{test_user_auth.id}/role/?role={role}",
                            headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"})
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Success"}

    user = asyncio.run(get_test_user_auth(test_user_auth.id))
    assert user.role_name == role


def test_search_user(client, test_user_auth, get_user_tokens):
    param = ""
    has_posts = True
    offset = 0
    limit = 10
    response = client.get(f"/api/admin/user/search/?search_param={param}&has_posts={has_posts}&offset={offset}&limit={limit}",
                          headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"})
    assert response.status_code == 200, response.text
    data = response.json()

    assert data[0]["post_count"] == 1
    assert data[0]["id"] == test_user_auth.id
