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

    async def get_posts(self, limit: int, offset: int, keyword: str, tag: str):
        stmt = select(Post)
        conditions = []

        if tag:
            conditions.append(Post.tags.any(Tag.name == tag))
        if keyword:
            conditions.append(Post.description.ilike(f"%{keyword}%"))
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.options(selectinload(Post.tags)).offset(offset).limit(limit)

        posts = await self.session.execute(stmt)
        return posts.scalars().all()

    async def get_post_by_id(self, post_id: int):
        stmt = select(Post).where(Post.id == post_id)
        post = await self.session.execute(stmt)
        return post.scalar_one_or_none()


    async def delete_post(self, post: Post):
        await self.session.delete(post)
        await self.session.commit()
        return post


    async def update_post_description(self, post: Post, description: str):
        post.description = description
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def create_post(
        self, user: User, description: str, tags: set[Tag], images: dict
    ):
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
