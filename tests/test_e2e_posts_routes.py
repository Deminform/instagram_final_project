from unittest.mock import patch

import pytest
from docutils.nodes import description
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from main import app
from src.users.models import User


@pytest.mark.asyncio
async def test_create_post(test_user, override_get_db, get_user_tokens, file_fixture):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

        payload = {
            "description":"Test post description",
            "user_id":1,
            "image_filter": "sepia",
            "original_image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/v1735225152/first_app/f283fba11972428993afc5f5fc165ad8.jpg",
            "image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/e_sepia/c_fill,h_1200,w_800/v1/first_app/f283fba11972428993afc5f5fc165ad8",
            "tags":("tag_1", "tag_2")
        }

        response = await client.post(
            "api/posts/",
            data=payload,
            files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
            headers={"Authorization": f"Bearer {get_user_tokens["access_token"]}"},
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["description"] == "Test post description"
        assert data["user_id"] == test_user.id


# def test_create_post(client, get_user_tokens, file_fixture):
#     payload = {
#         "description":"Test post description",
#         "user_id":1,
#         "image_filter": "sepia",
#         "original_image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/v1735225152/first_app/f283fba11972428993afc5f5fc165ad8.jpg",
#         "image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/e_sepia/c_fill,h_1200,w_800/v1/first_app/f283fba11972428993afc5f5fc165ad8",
#         "tags":("tag_1", "tag_2")
#     }
#
#     response = client.post(
#         "api/posts/",
#         data=payload,
#         files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
#         headers={"Authorization": f"Bearer {get_user_tokens["access_token"]}"},
#     )
#
#     assert response.status_code == 201, response.text
#     data = response.json()
#     assert data["description"] == "Test post description"
#     assert data["user_id"] == 1
