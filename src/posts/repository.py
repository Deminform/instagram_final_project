from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.posts.models import Post
from src.tags.models import Tag
from src.users.models import User


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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

        posts = await self.db.execute(stmt)
        return posts.scalars().all()

    async def get_post_by_id(self, post_id: int):
        stmt = select(Post).where(Post.id == post_id)
        post = await self.db.execute(stmt)
        return post.scalar_one_or_none()

    async def delete_post(self, user: User, post_id: int):
        stmt = (
            select(Post)
            .where(Post.id == post_id, Post.user_id == user.id)
            .with_for_update(nowait=True)
        )
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            await self.db.delete(post)
            await self.db.commit()
        return post

    async def update_post_description(self, user: User, post_id: int, description: str):
        stmt = (
            select(Post)
            .where(Post.id == post_id, Post.user_id == user.id)
            .with_for_update(nowait=True)
        )
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            post.description = description
            await self.db.commit()
            await self.db.refresh(post)
        return post

    async def create_post(
        self, user: User, description: str, tags: set[Tag], images: dict
    ):
        post = Post(
            description=description,
            user_id=user.id,
            original_image_url=images["original"],
            image_url=images["edited"],
        )
        post.tags = tags
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post
