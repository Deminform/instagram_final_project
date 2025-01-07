from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from conf import const
from src.posts.models import Post
from src.tags.models import Tag
from src.users.models import User


class PostRepository:

    def __init__(self, db: AsyncSession):
        self.session = db

    async def create_post(self, user: User, description: str, tags: set[Tag], images: dict) -> Post:
        """
        Create a new post with the provided user, description, tags, and images.

        :param user: The User instance creating the post.
        :param description: The description of the post.
        :param tags: A set of Tag instances associated with the post.
        :param images: A dictionary containing URLs of the original and edited images.
        :return: The created Post instance.
        """
        post = Post(
            description=description,
            user_id=user.id,
            original_image_url=images[const.ORIGINAL_IMAGE_URL],
            image_url=images[const.EDITED_IMAGE_URL],
        )
        post.tags = tags
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post


    async def get_post_by_id(self, post_id: int) -> Post:
        """
        Retrieve a post by its ID.

        :param post_id: The unique identifier of the post.
        :return: The Post instance if found, otherwise None.
        """
        stmt = select(Post).where(Post.id == post_id)
        post = await self.session.execute(stmt)
        return post.scalars().unique().one_or_none()


    async def get_posts(self, limit: int, offset: int, keyword: str, tag: str) -> list[Post]:
        """
        Retrieve a list of posts with optional filters and pagination.

        :param limit: The maximum number of posts to return.
        :param offset: The number of posts to skip.
        :param keyword: A keyword to filter posts by description.
        :param tag: A tag to filter posts by associated tags.
        :return: A list of Post instances matching the criteria.
        """
        stmt = select(Post)
        conditions = []
        if tag:
            conditions.append(Post.tags.any(Tag.name.ilike(f"%{tag}%")))
        if keyword:
            conditions.append(Post.description.ilike(f"%{keyword}%"))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.options(selectinload(Post.tags)).offset(offset).limit(limit)
        posts = await self.session.execute(stmt)
        return list(posts.scalars().all())


    async def update_post_description(self, post: Post, description: str) -> Post:
        """
        Update the description of a post.

        :param post: The Post instance to update.
        :param description: The new description for the post.
        :return: The updated Post instance.
        """
        post.description = description
        await self.session.commit()
        await self.session.refresh(post)
        return post


    async def delete_post(self, post: Post) -> Post:
        """
        Delete a post from the database.

        :param post: The Post instance to delete.
        :return: The deleted Post instance.
        """
        await self.session.delete(post)
        return post
