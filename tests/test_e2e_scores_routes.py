import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from main import app
from src.scores.models import Score
from src.scores.schemas import ScoreCreate, ScoreUpdate, AverageScore
from src.users.schemas import UserResponse, RoleEnum
from src.services.auth.auth_service import get_current_user
from src.scores.score_service import ScoreService
from database.db import get_db

from anyio import create_task_group, run
from httpx import AsyncClient
from unittest.mock import AsyncMock

@pytest.fixture
def mock_score_service():
    mock_service = AsyncMock(spec=ScoreService)
    mock_service.calculate_average_score.return_value = 4.5  # Мокуємо результат
    return mock_service

# Фікстури для тестів
@pytest.fixture
def test_user():
    return UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        role_name=RoleEnum.USER.value,
        first_name="Test",
        last_name="User",
        avatar_url="https://example.com/avatar.jpg",
        is_confirmed=True,
        is_banned=False,
        created_at=datetime.now()
    )

@pytest.fixture
def admin_user():
    return UserResponse(
        id=2,
        username="admin",
        email="admin@example.com",
        role_name=RoleEnum.ADMIN.value,
        first_name="Admin",
        last_name="User",
        avatar_url="https://example.com/avatar.jpg",
        is_confirmed=True,
        is_banned=False,
        created_at=datetime.now()
    )

@pytest.fixture
def mock_get_current_user(test_user):
    def _mock_get_current_user():
        return test_user
    return _mock_get_current_user

@pytest.fixture
def mock_get_current_admin(admin_user):
    def _mock_get_current_admin():
        return admin_user
    return _mock_get_current_admin


@pytest.fixture
def mock_score_service():
    class MockScoreService:
        async def fetch_score_by_id(self, score_id: int):
            if score_id == 1:
                return {"id": 1, "post_id": 1, "user_id": 1, "score": 4}
            return None

        async def fetch_scores_by_user(self, user_id: int, limit: int, offset: int):
            return [
                Score(id=1, post_id=1, user_id=user_id, score=4),
                Score(id=2, post_id=2, user_id=user_id, score=5),
            ]
        def fetch_scores_by_post(self, post_id: int, limit: int, offset: int):
            return [{"id": 1, "post_id": post_id, "user_id": 1, "score": 4}]

        async def create_new_score(self, score_data: ScoreCreate):
            return {"id": 3, **score_data.dict()}

        def update_existing_score(self, score_id: int, score_data: ScoreUpdate):
            return {"id": score_id, "post_id": 1, "user_id": 1, "score": score_data.score}

        def delete_existing_score(self, score_id: int):
            return True

        async def calculate_average_score(self, post_id: int):
            return 4.5

    return MockScoreService()

# Тести
def test_read_score(client, get_user_tokens, mock_score_service):
    # Перевизначення залежностей
    app.dependency_overrides[ScoreService] = lambda db: mock_score_service

    try:
        # Виклик маршруту з авторизацією
        response = client.get(
            "/api/scores/1",
            headers={"Authorization": f"Bearer {get_user_tokens['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["id"] == 1
        assert data["score"] == 4
    finally:
        # Очищення залежностей
        app.dependency_overrides.clear()

# def test_read_scores_by_user(client: TestClient, get_user_tokens, mock_score_service):
#     # Перевизначення залежностей
#     app.dependency_overrides[get_current_user] = lambda: UserResponse(
#         id=1,
#         username="testuser",
#         email="test@example.com",
#         role_name=RoleEnum.USER.value,
#         first_name="Test",
#         last_name="User",
#         avatar_url="https://example.com/avatar.jpg",
#         is_confirmed=True,
#         is_banned=False,
#         created_at=datetime.now()
#     )
#     app.dependency_overrides[ScoreService] = lambda db: mock_score_service

#     try:
#         headers = {"Authorization": f"Bearer {get_user_tokens['access_token']}"}
#         response = client.get("/api/scores/user/1", headers=headers)
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert isinstance(data, list)
#         assert len(data) == 2
#         assert data[0]["user_id"] == 1
#     finally:
#         # Очищення залежностей
#         app.dependency_overrides.clear()
    

def test_read_scores_by_post(client: TestClient, mock_score_service):
    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        role_name=RoleEnum.USER.value,
        first_name="Test",
        last_name="User",
        avatar_url="https://example.com/avatar.jpg",
        is_confirmed=True,
        is_banned=False,
        created_at=datetime.now()
    )
    app.dependency_overrides[ScoreService] = lambda db: mock_score_service

    response = client.get("api/scores/post/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["post_id"] == 1

# def test_create_new_score(client, mock_score_service):
#     app.dependency_overrides[get_current_user] = lambda: UserResponse(
#         id=1,
#         username="testuser",
#         email="test@example.com",
#         role_name=RoleEnum.USER.value,
#         first_name="Test",
#         last_name="User",
#         avatar_url="https://example.com/avatar.jpg",
#         is_confirmed=True,
#         is_banned=False,
#         created_at=datetime.now()
#     )
#     app.dependency_overrides[ScoreService] = lambda db: mock_score_service

#     payload = {"post_id": 1, "user_id": 1, "score": 5}

#     # Використовуємо anyio.run для запуску асинхронного коду в синхронному контексті
#     async def _run_test():
#         response = client.post("/api/scores/", json=payload)
#         assert response.status_code == status.HTTP_201_CREATED
#         data = response.json()
#         assert data["post_id"] == payload["post_id"]
#         assert data["user_id"] == payload["user_id"]
#         assert data["score"] == payload["score"]

#     run(_run_test)

# def test_update_existing_score(client: TestClient, mock_score_service):
#     app.dependency_overrides[get_current_user] = lambda: UserResponse(
#         id=1,
#         username="testuser",
#         email="test@example.com",
#         role_name=RoleEnum.USER.value,
#         first_name="Test",
#         last_name="User",
#         avatar_url="https://example.com/avatar.jpg",
#         is_confirmed=True,
#         is_banned=False,
#         created_at=datetime.now()
#     )
#     app.dependency_overrides[ScoreService] = lambda db: mock_score_service

#     payload = {"score": 3}
#     response = client.put("api/scores/1", json=payload)
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["id"] == 1
#     assert data["score"] == payload["score"]

# def test_delete_existing_score(client: TestClient, mock_score_service, mock_get_current_admin):
#     app.dependency_overrides[get_current_user] = mock_get_current_admin
#     app.dependency_overrides[ScoreService] = lambda db: mock_score_service

#     response = client.delete("api/scores/1")
#     assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_existing_score_unauthorized(client: TestClient, mock_score_service, mock_get_current_user):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[ScoreService] = lambda db: mock_score_service

    response = client.delete("/api/scores/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN

# def test_get_post_average_score(client: TestClient, mock_score_service):
#     app.dependency_overrides[get_current_user] = lambda: UserResponse(
#         id=1,
#         username="testuser",
#         email="test@example.com",
#         role_name=RoleEnum.USER.value,
#         first_name="Test",
#         last_name="User",
#         avatar_url="https://example.com/avatar.jpg",
#         is_confirmed=True,
#         is_banned=False,
#         created_at=datetime.now()
#     )
#     app.dependency_overrides[ScoreService] = lambda db: mock_score_service

#     # Виклик маршруту
#     response = client.get("/api/scores/post/1/average")
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["post_id"] == 1
#     assert data["average_score"] == 4.5
