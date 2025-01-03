import pytest
import pytest_asyncio
from sqlalchemy import select

from conf import messages
from src.posts.models import Post
from src.comments.models import Comment
from src.comments.repository import CommentRepository
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import TestingSessionLocal


@pytest_asyncio.fixture(scope="module")
async def create_test_post(get_user):
    user = get_user
    async with TestingSessionLocal() as session:
        post = Post(
            id=1,
            description="Test post description",
            user_id=user.id,
            original_image_url="https://example.com/test_original_image.jpg",
            image_url="https://example.com/test_image.jpg",
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
    return post


@pytest_asyncio.fixture()
async def create_test_comment(get_user):
    user = get_user
    async with TestingSessionLocal() as session:
        comment = Comment(
            post_id=1,
            user_id=user.id,
            comment="This is a test comment",
            is_update=False,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
    return comment


@pytest.mark.asyncio
async def test_add_comment(client, get_user_tokens, create_test_post):
    # Arrange
    comment_data = {"comment": "This is a test comment"}
    post = create_test_post

    # Act
    response = client.post(
        f"api/comments/{post.id}",
        json=comment_data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == comment_data["comment"]
    assert data["post_id"] == post.id
    assert "id" in data


@pytest.mark.asyncio
async def test_add_comment_no_post(client, get_user_tokens):
    comment_data = {"comment": "This is a test comment"}
    post_id = 2

    response = client.post(
        f"api/comments/{post_id}",
        json=comment_data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.POST_NOT_FOUND


@pytest.mark.asyncio
async def test_edit_comment(client, get_user_tokens):
    comment_data = {
        "comment": "This is a update comment",
        "is_update": True,
    }
    comment_id = 1

    response = client.put(
        f"api/comments/{comment_id}",
        json=comment_data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == comment_data["comment"]
    assert data["is_update"] == True
    assert data["id"] == comment_id


@pytest.mark.asyncio
async def test_edit_comment_no(client, get_user_tokens):
    comment_data = {
        "comment": "This is a update comment",
        "is_update": True,
    }
    comment_id = 2

    response = client.put(
        f"api/comments/{comment_id}",
        json=comment_data,
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_COMMENT


@pytest.mark.asyncio
async def test_delete_comment(client, get_user_tokens, create_test_comment):
    comment = create_test_comment

    response = client.delete(
        f"/api/comments/{comment.id}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 204, f"Expected 204, but got {response.status_code}"

    async with TestingSessionLocal() as session:
        check_comment_repo = CommentRepository(session)
        deleted_comment = await check_comment_repo.delete_comment(comment.id)
        assert deleted_comment is None, f"Comment {comment.id} was not deleted"


@pytest.mark.asyncio
async def test_delete_comment_no(client, get_user_tokens):
    comment_id = 2

    response = client.delete(
        f"/api/comments/{comment_id}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_COMMENT


@pytest.mark.asyncio
async def test_get_comment_by_post_all(client, get_user_tokens, create_test_comment):
    post_id = 1
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/{post_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    for comment_data in data:
        assert comment_data["post_id"] == post_id


@pytest.mark.asyncio
async def test_get_comment_by_post_all_no(client, get_user_tokens):
    post_id = 2
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/{post_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_COMMENT


@pytest.mark.asyncio
async def test_get_comment_by_post_user(client, get_user_tokens, create_test_comment):
    post_id = 1
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/user/{post_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    for comment_data in data:
        assert comment_data["post_id"] == post_id


@pytest.mark.asyncio
async def test_get_comment_by_post_user_no(client, get_user_tokens):
    post_id = 3
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/user/{post_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.POST_NOT_FOUND


@pytest.mark.asyncio
async def test_get_comment_by_post_author(client, get_user_tokens, create_test_comment):
    user_id = 1
    post_id = 1
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/admin/{post_id}/{user_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    for comment_data in data:
        assert comment_data["post_id"] == post_id


@pytest.mark.asyncio
async def test_get_comment_by_post_author_no(client, get_user_tokens):
    user_id = 2
    post_id = 1
    limit = 10
    offset = 0

    response = client.get(
        f"/api/comments/admin/{post_id}/{user_id}?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Not Found"
