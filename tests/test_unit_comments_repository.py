import unittest
import pytest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy import extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import Role, Token, User

from src.comments.schema import CommentBase
from src.comments.repository import CommentRepository
from src.comments.models import Comment
from src.comments.comments_services import CommentServices


class TestAsyncComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            id=1,
            first_name="Firstname",
            last_name="Lastname",
            phone="+380675554433",
            username="test_user",
            email="test@gmail.com",
            password="123456789",
            is_confirmed=True,
        )
        self.session = AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_add_comment(self):
        post_id = 1
        body = CommentBase(comment="test comment")

        reposytory = CommentRepository(self.session)
        result = await reposytory.add_comment(post_id, body, self.user)
        self.assertIsInstance(result, Comment)
        self.assertEqual(result.comment, body.comment)
        self.assertEqual(result.post_id, post_id)
