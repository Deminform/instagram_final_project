from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post
from src.posts.schemas import PostSchema
from src.tags.models import Tag
from src.users.models import User



class TagRepository:
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


