import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from conf import const
from src.posts.models import Post
from src.posts.repository import PostRepository
from src.tags.models import Tag
from src.users.models import User

faker = Faker()


class TestContacts(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User(
            id=1,
            first_name='Steve',
            last_name='Johnson',
            email="steve@testmail.com",
            username='Steve789',
            phone="123654987",
            avatar_url="https://avatars.githubusercontent.com/u/1026217?s=460&v=4",
            role_id=1,  # 1 - admin, 2 - moderator, 3 - user
            is_banned=False,
            is_confirmed=True,
        )

        cls.tags = {Tag(id=1, name="tag_1"), Tag(id=2, name="tag_2")}

        cls.images = {
            const.ORIGINAL_IMAGE_URL: "https://res.cloudinary.com/dr0qfbx4m/image/upload/v1735225152/first_app/f283fba11972428993afc5f5fc165ad8.jpg",
            const.EDITED_IMAGE_URL: "https://res.cloudinary.com/dr0qfbx4m/image/upload/e_sepia/c_fill,h_1200,w_800/v1/first_app/f283fba11972428993afc5f5fc165ad8",
        }

        cls.post = Post(
            description="Test description",
            user_id=cls.user.id,
            original_image_url=cls.images[const.ORIGINAL_IMAGE_URL],
            image_url=cls.images[const.EDITED_IMAGE_URL],
        )
        cls.post.tags = cls.tags
        cls.post_2 = Post(
            description="Test description 2",
            user_id=cls.user.id,
            original_image_url=cls.images[const.ORIGINAL_IMAGE_URL],
            image_url=cls.images[const.EDITED_IMAGE_URL],
        )

        cls.post_2.tags = cls.tags

        cls.description = "Test description 3"

    @classmethod
    def tearDownClass(cls):
        ...

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.session.execute = AsyncMock()
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.post_repository = PostRepository(self.session)


    def tearDown(self):
        ...


    async def test_create_post(self):
        post = await self.post_repository.create_post(self.user, self.post.description, self.tags, self.images)
        self.session.add.assert_called_once_with(post)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(post)
        self.assertEqual(post.description, self.post.description)
        self.assertEqual(post.user_id, self.user.id)
        self.assertEqual(post.tags, self.tags)
        self.assertEqual(post.original_image_url, self.images[const.ORIGINAL_IMAGE_URL])
        self.assertEqual(post.image_url, self.images[const.EDITED_IMAGE_URL])
        self.assertIsInstance(post, Post)


    async def test_get_post_by_id(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.one_or_none.return_value = self.post
        self.session.execute.return_value = mock_result

        post = await self.post_repository.get_post_by_id(self.post.id)

        self.session.execute.assert_awaited_once()

        args, kwargs = self.session.execute.call_args
        actual_stmt = args[0]
        self.assertIsInstance(actual_stmt, Select)

        expected_condition = (Post.id == self.post.id)
        actual_where = actual_stmt._whereclause

        self.assertEqual(str(actual_where), str(expected_condition))

        self.assertEqual(post.description, self.post.description)
        self.assertEqual(post.user_id, self.user.id)
        self.assertEqual(post.tags, self.tags)

    async def test_get_posts(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.post, self.post_2]
        self.session.execute.return_value = mock_result

        # Case 1: neither tag nor keyword is specified
        limit = 5
        offset = 10
        keyword = None
        tag = None

        posts = await self.post_repository.get_posts(limit, offset, keyword, tag)
        self.session.execute.assert_awaited_once()
        args, kwargs = self.session.execute.call_args
        actual_stmt = args[0]
        self.assertIsInstance(actual_stmt, Select)
        compiled = actual_stmt.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)
        self.assertNotIn("WHERE", sql)
        self.assertIn(f"LIMIT {limit}", sql)
        self.assertIn(f"OFFSET {offset}", sql)
        self.assertEqual(len(posts), 2)

        # Case 2: only tag specified
        tag = "test"
        keyword = None

        posts = await self.post_repository.get_posts(limit, offset, keyword, tag)
        args, kwargs = self.session.execute.call_args
        actual_stmt = args[0]
        compiled = actual_stmt.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)
        self.assertIn(f"lower(tags.name) LIKE lower('%{tag}%')", sql)  # Обновлённое условие
        self.assertNotIn("Post.description", sql)

        # Case 3: only the keyword is specified
        tag = None
        keyword = "description"

        posts = await self.post_repository.get_posts(limit, offset, keyword, tag)
        args, kwargs = self.session.execute.call_args
        actual_stmt = args[0]
        compiled = actual_stmt.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)

        self.assertIn(f"lower(posts.description) LIKE lower('%{keyword}%')", sql)  # Обновлённое условие
        self.assertNotIn("Tag.name", sql)

        # Case 4: both are indicated
        tag = "test"
        keyword = "description"

        posts = await self.post_repository.get_posts(limit, offset, keyword, tag)
        args, kwargs = self.session.execute.call_args
        actual_stmt = args[0]
        compiled = actual_stmt.compile(compile_kwargs={"literal_binds": True})
        sql = str(compiled)
        self.assertIn(f"lower(tags.name) LIKE lower('%{tag}%')", sql)  # Обновлённое условие
        self.assertIn(f"lower(posts.description) LIKE lower('%{keyword}%')", sql)

    async def test_update_post(self):
        post = await self.post_repository.update_post_description(self.post, self.description)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(post)
        self.assertEqual(post.description, self.description)
        self.assertIsInstance(post, Post)

    async def test_delete_post(self):
        post = await self.post_repository.delete_post(self.post)
        self.session.delete.assert_called_once_with(post)
        self.session.commit.assert_called_once()
        self.assertEqual(post.description, self.post.description)
        self.assertIsInstance(post, Post)

