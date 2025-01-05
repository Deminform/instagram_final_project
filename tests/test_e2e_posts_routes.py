from unittest.mock import patch

import pytest
from docutils.nodes import description
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from conf import messages
from main import app
from src.users.models import User


# @pytest.mark.asyncio
# async def test_create_post(test_user, override_get_db, get_user_tokens, file_fixture):
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#
#         payload = {
#             "description":"Test post description",
#             "user_id":1,
#             "image_filter": "sepia",
#             "original_image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/v1735225152/first_app/f283fba11972428993afc5f5fc165ad8.jpg",
#             "image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/e_sepia/c_fill,h_1200,w_800/v1/first_app/f283fba11972428993afc5f5fc165ad8",
#             "tags":("tag_1", "tag_2")
#         }
#
#         response = await client.post(
#             "api/posts/",
#             data=payload,
#             files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
#             headers={"Authorization": f"Bearer {get_user_tokens["access_token"]}"},
#         )
#
#         assert response.status_code == 201, response.text
#         data = response.json()
#         assert data["description"] == "Test post description"
#         assert data["user_id"] == test_user.id


def test_create_post_success(client, get_user_tokens, file_fixture):
    payload = {
        "description": "Test post description",
        "user_id": 1,
        "image_filter": "sepia",
        "original_image_url": "https://res.cloudinary.com/example/original.jpg",
        "image_url": "https://res.cloudinary.com/example/edited.jpg",
        "tags": ("tag_1", "tag_2"),
    }

    response = client.post(
        "api/posts/",
        data=payload,
        files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["description"] == payload["description"]
    assert data["user_id"] == 1
    global POST_ID
    POST_ID = data["id"]


def test_create_post_bad_filter(client, get_user_tokens, file_fixture):
    payload = {
        "description": "Bad filter test",
        "image_filter": "bad_filter",
        "tags": ("tag_1", "tag_2"),
    }

    response = client.post(
        "api/posts/",
        data=payload,
        files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == messages.FILTER_IMAGE_ERROR_DETAIL


def test_create_post_too_short_description(client, get_user_tokens, file_fixture):
    payload = {"description": "H", "tags": ("tag_1", "tag_2")}
    response = client.post(
        "api/posts/",
        data=payload,
        files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"][0]["msg"] == "String should have at least 2 characters"


def test_create_post_no_auth(client, file_fixture):
    payload = {"description": "No auth description", "tags": ("tag_1", "tag_2")}
    response = client.post(
        "api/posts/",
        data=payload,
        files={"image": (file_fixture.name, file_fixture, "image/jpeg")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_get_posts(client, get_user_tokens):
    response = client.get(
        "api/posts/",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_post_by_id(client, get_user_tokens):
    response = client.get(
        f"api/posts/{POST_ID}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == POST_ID
    assert data["description"] == "Test post description"


def test_get_post_not_found(client, get_user_tokens):
    response = client.get(
        "api/posts/99999",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Post not found"


def test_edit_post(client, get_user_tokens):
    new_description = "Updated description"
    response = client.put(
        f"api/posts/{POST_ID}",
        json={"description": new_description},
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == POST_ID
    assert data["description"] == new_description


def test_create_qr(client, get_user_tokens):
    params = {"image_filter": "sepia"}
    response = client.post(
        f"api/posts/{POST_ID}/qr",
        params=params,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/png"


def test_create_qr_bad_filter(client, get_user_tokens):
    params = {"image_filter": "invalid_filter"}
    response = client.post(
        f"api/posts/{POST_ID}/qr",
        params=params,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == messages.FILTER_IMAGE_ERROR_DETAIL


def test_delete_post_unauthorized(client):
    response = client.delete(f"api/posts/{POST_ID}")
    assert response.status_code == 401, response.text


def test_delete_post(client, get_user_tokens):
    response = client.delete(
        f"api/posts/{POST_ID}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 204, response.text

    check_response = client.get(
        f"api/posts/{POST_ID}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert check_response.status_code == 404, check_response.text
