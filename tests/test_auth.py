import pytest
from unittest.mock import patch, AsyncMock
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from main import app
from src.users.models import Role


# @pytest.mark.asyncio
# async def test_user_registration(user_role: Role, override_get_db, faker):
#     with patch.object(BackgroundTasks, "add_task"):
#         async with AsyncClient(
#             transport=ASGITransport(app=app), base_url="http://test"
#         ) as ac:
#             payload = {
#                 "first_name": faker.first_name(),
#                 "last_name": faker.last_name(),
#                 "phone": faker.phone_number()[:15],
#                 "username": faker.user_name(),
#                 "email": faker.email(),
#                 "password": faker.password(),
#             }
#             response = await ac.post(
#                 "/api/auth/signup",
#                 json=payload,
#             )
#             assert response.status_code == 201
#             data = response.json()
#             assert data["email"] == payload["email"]
#             assert data["username"] == payload["username"]
#             assert data.get("password") is None
#             assert data["id"] is not None
#
#
# @pytest.mark.asyncio
# async def test_user_login(override_get_db, test_user, user_password):
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         response = await ac.post(
#             "/api/auth/login",
#             data={
#                 "username": test_user.email,
#                 "password": user_password,
#             },
#         )
#         print(response)
#         assert response.status_code == 200
#         data = response.json()
#         assert "access_token" in data
#         assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_user_by_id(
    override_get_db, test_user, auth_header
):

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        print(f"Request Headers: {auth_header}")
        # Then, retrieve the user by ID
        response = await ac.get(
            f"/api/users/{test_user.id}", headers=auth_header
        )

    assert response.status_code == 200
    # data = response.json()
    # assert data["first_name"] == test_user.first_name
    # assert data["last_name"] == test_user.last_name