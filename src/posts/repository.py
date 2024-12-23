from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments.models import Comment
from src.images.models import Image
from src.posts.models import Post, Tag
from src.posts.schemas import PostSchema, PostUpdateSchema
from src.users.models import User


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_post_by_filter(self, db: AsyncSession, user_id: int = None, limit: int = 10, offset: int = 0):
        stmt = select(Post)
        if user_id:
            stmt = select(Post).where(Post.user_id == user_id)
        stmt = stmt.offset(offset).limit(limit)
        posts = await db.execute(stmt)
        result = posts.scalars().all()
        return result


    async def get_post_by_id(self, db: AsyncSession, user: User, post_id: int = None):
        stmt = select(Post).where(Post.id == post_id)
        post = await db.execute(stmt)
        result = post.scalar_one_or_none()
        return result


    async def create_post(self, db: AsyncSession, user: User, body: PostSchema, image: Image):
        post = Post(user_id=user.id, description=body.description)
        db.add(post)

        tags = await get_or_create_tags(db, body.tags)

        post.tags.update(tags)
        post.images.add(image)

        await db.commit()
        await db.refresh(post)
        return post


    async def create_tag(self, db: AsyncSession, tag_name: str):
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag


    async def get_tags_by_names(self, db: AsyncSession, tags_list: set[str]) -> set[Tag]:
        stmt = select(Tag).where(Tag.name.in_(tags_list))
        tag = await db.execute(stmt)
        result = set(tag.scalars().all())
        return result


    async def delete_post(self, db: AsyncSession, user: User, post_id: int):
        stmt = (
            select(Post)
            .where(Post.id == post_id, Post.user_id == user.id)
            .with_for_update(nowait=True)
        )
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            await db.delete(post)
            await db.commit()
        return post


    async def update_post(self, db: AsyncSession, user: User, post_id: int, body: PostUpdateSchema, comment: Comment = None,
                          average_score: float = None, image: Image = None):
        post = await get_post_by_id(db, user, post_id)
        if post:
            if body.description:
                post.description = body.description
            if comment:
                post.comments.add(comment)
            if body.tags:
                tags = await get_or_create_tags(db, body.tags)
                post.tags.update(tags)
            if average_score:
                post.score_result = average_score
            if image:
                post.images.add(image)

        await db.commit()
        await db.refresh(post)
        return post


    async def get_or_create_tags(self, db: AsyncSession, tags: set[str]):
        tags_list = await get_tags_by_names(db, tags)
        existing_tag_names = {tag.name for tag in tags_list}
        not_existing_tag_names = [tag for tag in tags if tag not in existing_tag_names]
        for tag in not_existing_tag_names:
            tag_obj = await create_tag(db, tag)
            tags_list.add(tag_obj)
        return tags_list

