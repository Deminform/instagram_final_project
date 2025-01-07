import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from src.urls.models import URLs
from src.urls.repository import URLRepository

from faker import Faker

class TestAsyncURLs(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = URLs(
            id=1,
            post_id=1,
            image_url="http://example.com/image1.png",
            image_filter="grayscale",
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        self.session = MagicMock(spec=AsyncSession)
        self.session.execute = AsyncMock()
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.session.delete = AsyncMock()
        self.url_repository = URLRepository(self.session)

    def tearDown(self):
        pass

    async def test_add_image(self):
        post_id = 1
        image_url = "http://example.com/image1.png"
        image_filter = "grayscale"

        result = await self.url_repository.add_image(post_id, image_url, image_filter)

        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.assertEqual(result.post_id, post_id)
        self.assertEqual(result.image_url, image_url)
        self.assertEqual(result.image_filter, image_filter)

    async def test_get_image(self):
        self.session.execute.return_value.scalar_one_or_none = lambda: self.url

        result = await self.url_repository.get_image(
            post_id=self.url.post_id, image_filter=self.url.image_filter
        )

        self.session.execute.assert_called_once()
        self.assertEqual(result.post_id, self.url.post_id)
        self.assertEqual(result.image_url, self.url.image_url)
        self.assertEqual(result.image_filter, self.url.image_filter)

    async def test_get_image_not_found(self):
        self.session.execute.return_value.scalar_one_or_none = lambda: None

        result = await self.url_repository.get_image(post_id=2, image_filter="grayscale")

        self.session.execute.assert_called_once()
        self.assertIsNone(result)

    async def test_delete_urls_by_post_id(self):
        post_id = 1
        self.session.execute.return_value = AsyncMock()

        await self.url_repository.delete_urls_by_post_id(post_id=post_id)

        self.session.execute.assert_called_once()
        self.session.commit.assert_awaited_once()

        # Verify the SQL query contains the correct delete statement
        called_stmt = self.session.execute.call_args[0][0]
        self.assertIsInstance(called_stmt, delete)
        self.assertEqual(called_stmt.whereclause.left.key, "post_id")
        self.assertEqual(called_stmt.whereclause.right.value, post_id)