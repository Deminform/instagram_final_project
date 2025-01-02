import unittest
import pytest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy import extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import Role, Token, User

from conf import const
from src.posts.models import Post
from src.comments.schema import CommentBase
from src.comments.repository import CommentRepository
from src.comments.models import Comment
from src.comments.comments_services import CommentService


class TestAsyncComments(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User(
            id=1,
            first_name="Test",
            last_name="Testing",
            email="test@testmail.com",
            username="test1234",
            phone="123654987",
            avatar_url="https://avatars.githubusercontent.com/u/1026217?s=460&v=4",
            role_id=1,
            is_banned=False,
            is_confirmed=True,
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.session.execute = AsyncMock()
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.comment_repository = CommentRepository(self.session)

    def tearDown(self):
        pass

    @pytest.mark.asyncio
    async def test_add_comment(self):
        post_id = 1
        body = CommentBase(comment="test comment")

        result = await self.comment_repository.add_comment(post_id, body, self.user)
        self.assertIsInstance(result, Comment)
        self.assertEqual(result.comment, body.comment)
        self.assertEqual(result.post_id, post_id)

    # @pytest.mark.asyncio
    # async def test_edit_comment(self):
    #     # Arrange
    #     comment_id = 1
    #     body = CommentBase(comment="updated comment")

    #     comment = Comment(
    #         id=comment_id,
    #         post_id=self.post.id,
    #         user_id=self.user.id,
    #         comment="original comment",
    #         is_update=False,
    #     )

    #     # Mock the database response
    #     stmt = select(Comment).filter(Comment.id == comment_id, Comment.user_id == self.user.id)

    #     execute_result = MagicMock()
    #     execute_result.scalar_one_or_none = AsyncMock(return_value=comment)
    #     self.session.execute = AsyncMock(return_value=execute_result)

    #     # Act
    #     result = await self.comment_repository.edit_comment(comment_id, body, self.user)

    #     # Assert
    #     self.session.execute.assert_called_once_with(stmt)
    #     self.session.commit.assert_called_once()
    #     self.session.refresh.assert_called_once_with(comment)
    #     self.assertEqual(result.comment, body.comment)
    #     self.assertTrue(result.is_update)
    #     self.assertEqual(result.id, comment_id)
