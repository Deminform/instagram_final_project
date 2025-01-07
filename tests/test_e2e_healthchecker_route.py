import pytest
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient

from conf import messages
from database.db import get_db
from main import app


@pytest_asyncio.fixture(scope="function")
async def mock_db_session():
    class MockResult:
        async def fetchone(self):
            return None  # Эмулируем пустой результат

    class MockSession:
        async def execute(self, query):
            print("DEBUG: Mock execute called")  # Для проверки вызова
            return MockResult()

        async def close(self):
            pass

    return MockSession()


@pytest.mark.asyncio
async def test_healthchecker_success():
    with TestClient(app) as test_client:
        response = test_client.get("api/healthchecker/")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["message"] == "Database is healthy"


@pytest.mark.asyncio
async def test_healthchecker_db_raises_exception():
    async def mock_get_db():
        class MockSession:
            async def execute(self, query):
                raise Exception("Database error")
            async def close(self):
                pass
        yield MockSession()

    app.dependency_overrides[get_db] = mock_get_db

    with TestClient(app) as test_client:
        response = test_client.get("api/healthchecker/")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
        data = response.json()
        assert "Database error" in data["detail"]

    app.dependency_overrides.pop(get_db, None)
