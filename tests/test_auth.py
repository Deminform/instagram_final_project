import pytest
from unittest.mock import patch
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from main import app
from src.users.models import Role
from tests.conftest import test_user_dict


def test_user_registration(client, faker):
    with patch.object(BackgroundTasks, "add_task") as mock_add_task:
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "phone": faker.phone_number()[:15],
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
        assert data["role_name"] is not None
        assert data["avatar_url"] is not None
        assert data["is_confirmed"] == False
        assert data["is_banned"] == False
        mock_add_task.assert_called_once()


# def test_user_login(client):
#     payload = {
#         "username": test_user_dict["email"],
#         "password": test_user_dict["password"]
#
#     }
#     print(f"Payload: {payload}")
#     response = client.post('api/auth/login', data=payload)
#     print(f"Response: {response.status_code} {response.text}")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     print(f"Response Data: {data}")
#     assert "access_token" in data
#     assert "refresh_token" in data


def test_get_user_by_id(client, get_user_tokens, get_user):
    response = client.get(f"/api/users/{1}", headers={'Authorization': f'Bearer {get_user_tokens}'})
    assert response.status_code == 200, response.text
    # data = response.json()
    # assert data['first_name'] == test_user_dict['first_name']
    # assert data['last_name'] == test_user_dict['last_name']
    # assert data['phone'] == test_user_dict['phone']
    # assert data['username'] == test_user_dict['username']
    # assert data['email'] == test_user_dict['email']
    # assert data.get("password") is None
    # assert data["id"] is not None
    # assert data["role_name"] == 'user'
    # assert data["avatar_url"] is not None
    # assert data["is_confirmed"] == True
    # assert data["is_banned"] == False