import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from conf import const
from src.posts.models import Post
from src.tags.repository import TagRepository
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

        cls.tag_1 = Tag(id=1, name="tag_1")
        cls.tag_2 = Tag(id=2, name="tag_2")
        cls.tag_3 = Tag(id=3, name="tag_3")
        cls.tag_4 = Tag(id=4, name="tag_4")
        cls.tag_5 = Tag(id=5, name="tag_5")
        cls.tag_6 = Tag(id=6, name="tag_6")


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

        cls.post_2 = Post(
            description="Test description 2",
            user_id=cls.user.id,
            original_image_url=cls.images[const.ORIGINAL_IMAGE_URL],
            image_url=cls.images[const.EDITED_IMAGE_URL],
        )

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
        self.tags_repository = TagRepository(self.session)


    def tearDown(self):
        ...


    async def test_create_tag(self):
        tag = await self.tags_repository.create_tag(self.tag_1.name)
        self.session.add.assert_called_once_with(tag)
        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()
        self.assertEqual(tag.name, self.tag_1.name)
        self.assertIsInstance(tag, Tag)

    async def test_get_tags_by_names(self):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.tag_1, self.tag_2]
        self.session.execute.return_value = mock_result
        tags_list = {"tag_1", "tag_2"}
        result = await self.tags_repository.get_tags_by_names(tags_list)
        self.session.execute.assert_called_once()
        stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Tag).where(Tag.name.in_(tags_list))
        self.assertEqual(str(stmt), str(expected_stmt))
        self.assertEqual(result, {self.tag_1, self.tag_2})
        self.assertIsInstance(result, set)

    async def test_delete_tag(self):
        tag_name = "tag_1"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.tag_1
        self.session.execute.return_value = mock_result
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()
        result = await self.tags_repository.delete_tag(tag_name)
        actual_stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Tag).where(Tag.name == tag_name)
        self.assertEqual(str(actual_stmt), str(expected_stmt))
        self.session.delete.assert_called_once_with(self.tag_1)
        self.session.commit.assert_called_once()
        self.assertEqual(result, self.tag_1)

    async def test_delete_tag_not_found(self):
        tag_name = "non_existing_tag"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()
        result = await self.tags_repository.delete_tag(tag_name)
        actual_stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Tag).where(Tag.name == tag_name)
        self.assertEqual(str(actual_stmt), str(expected_stmt))
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()
        self.assertIsNone(result)


