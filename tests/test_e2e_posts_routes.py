from conf import messages
from src.posts.schemas import PostResponseSchema


def test_create_post_success(client, get_user_tokens, file_fixture):
    payload = {
        "description": "Test post description",
        "user_id": 1,
        "image_filter": "grayscale",
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


def test_get_posts(client, get_user_tokens, create_post):
    response = client.get(
        "api/posts/",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_post_by_id(client, get_user_tokens, create_post):
    response = client.get(
        f"api/posts/{create_post.id}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    post_obj = PostResponseSchema(**data)
    assert post_obj.id == create_post.id
    assert post_obj.description == create_post.description
    assert isinstance(post_obj, PostResponseSchema)


def test_get_post_not_found(client, get_user_tokens):
    response = client.get(
        "api/posts/99999",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Post not found"


def test_edit_post(client, get_user_tokens, create_post):
    new_description = "Updated description"
    response = client.put(
        f"api/posts/{create_post.id}",
        json={"description": new_description},
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == create_post.id
    assert data["description"] == new_description


def test_create_qr(client, get_user_tokens, create_post):
    data = {"image_filter": "grayscale"}
    response = client.post(
        f"api/posts/{create_post.id}/qr",
        data=data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/png"


def test_create_qr_bad_filter(client, get_user_tokens, create_post):
    data = {"image_filter": "invalid_filter"}
    response = client.post(
        f"api/posts/{create_post.id}/qr",
        data=data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == messages.FILTER_IMAGE_ERROR_DETAIL


def test_delete_post_unauthorized(client, create_post):
    response = client.delete(f"api/posts/{create_post.id}")
    assert response.status_code == 401, response.text


def test_delete_post(client, get_user_tokens, create_post):
    response = client.delete(
        f"api/posts/{create_post.id}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert response.status_code == 204, response.text

    check_response = client.get(
        f"api/posts/{create_post.id}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )
    assert check_response.status_code == 404, check_response.text
