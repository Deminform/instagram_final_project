import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.comments.schema import CommentBase
from src.comments.repository import CommentRepository
from src.comments.models import Comment


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

        cls.comment_base = CommentBase(comment="Test comment")
        cls.comment = Comment(id=1, comment="Test comment", post_id=1, user_id=cls.user.id)

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
        self.comment_repository = CommentRepository(self.session)

    def tearDown(self):
        pass

    async def test_add_comment(self):
        post_id = 1

        result = await self.comment_repository.add_comment(
            post_id=post_id, body=self.comment_base, user=self.user
        )

        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
        self.assertEqual(result.comment, "Test comment")
        self.assertEqual(result.post_id, post_id)
        self.assertEqual(result.user_id, self.user.id)

    async def test_edit_comment(self):
        self.session.execute.return_value.scalar_one_or_none = lambda: self.comment

        result = await self.comment_repository.edit_comment(
            comment_id=1, body=self.comment_base, user=self.user
        )

        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
        self.assertEqual(result.comment, "Test comment")
        self.assertTrue(result.is_update)

    async def test_delete_comment(self):
        self.session.execute.return_value.scalar_one_or_none = lambda: self.comment  # ???

        result = await self.comment_repository.delete_comment(comment_id=1)

        self.session.delete.assert_awaited_once_with(self.comment)
        self.session.commit.assert_awaited_once()
        self.assertEqual(result, self.comment)

    async def test_get_comment_by_post_all(self):
        comments = [
            Comment(id=1, comment="Comment 1", post_id=1, user_id=1),
            Comment(id=2, comment="Comment 2", post_id=1, user_id=2),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = mock_result

        result = await self.comment_repository.get_comment_by_post_all(
            post_id=1, limit=10, offset=0
        )

    async def test_get_comment_by_post_user(self):
        comments = [
            Comment(id=1, comment="Comment 1", post_id=1, user_id=1),
            Comment(id=2, comment="Comment 2", post_id=1, user_id=1),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = mock_result

        result = await self.comment_repository.get_comment_by_post_user(
            post_id=1,
            limit=10,
            offset=0,
            user=self.user,
        )

        self.assertEqual(result, comments)

    async def test_get_comment_by_post_author(self):
        comments = [
            Comment(id=1, comment="Comment 1", post_id=1, user_id=1),
            Comment(id=2, comment="Comment 2", post_id=1, user_id=1),
            Comment(id=3, comment="Comment 3", post_id=1, user_id=2),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value = iter(
            [comment for comment in comments if comment.user_id == 1]
        )
        self.session.execute.return_value = mock_result

        result = await self.comment_repository.get_comment_by_post_author(
            post_id=1, user_id=1, limit=10, offset=0
        )

        expected_comments = [comment for comment in comments if comment.user_id == 1]
        self.assertEqual(len(result), len(expected_comments))
        self.assertListEqual(result, expected_comments)

        for comment in result:
            self.assertEqual(comment.user_id, 1)

        self.session.execute.assert_called_once()
        called_stmt = self.session.execute.call_args[0][0]
        where_conditions = list(called_stmt.whereclause)
        self.assertEqual(len(where_conditions), 2)

        post_id_condition = where_conditions[0]
        user_id_condition = where_conditions[1]
        self.assertEqual(post_id_condition.left.key, "post_id")
        self.assertEqual(post_id_condition.right.value, 1)
        self.assertEqual(user_id_condition.left.key, "user_id")
        self.assertEqual(user_id_condition.right.value, 1)

    async def test_exists_comment(self):
        self.session.execute.return_value.scalar_one_or_none = lambda: self.comment

        result = await self.comment_repository.exists_comment(comment="Test comment", user_id=1)

        self.assertEqual(result, self.comment)

    async def test_delete_comment_by_post_id(self):
        post_id = 1

        self.session.execute.return_value = AsyncMock()

        await self.comment_repository.delete_comment_by_post_id(post_id=post_id)
