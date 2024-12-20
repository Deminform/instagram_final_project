from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post
from src.posts.schemas import PostSchema
from src.tags.models import Tag
from src.users.models import User



class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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


    async def get_or_create_tags(self, db: AsyncSession, tags: set[str]):
        tags_list = await get_tags_by_names(db, tags)
        existing_tag_names = {tag.name for tag in tags_list}
        not_existing_tag_names = [tag for tag in tags if tag not in existing_tag_names]
        for tag in not_existing_tag_names:
            tag_obj = await create_tag(db, tag)
            tags_list.add(tag_obj)
        return tags_list
