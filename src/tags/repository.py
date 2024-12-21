from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import Tag


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tag(self, tag_name: str):
        tag = Tag(name=tag_name)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag


    async def get_tags_by_names(self, tags_list: set[str]) -> set[Tag]:
        stmt = select(Tag).where(Tag.name.in_(tags_list))
        result = await self.db.execute(stmt)
        tag = set(result.scalars().all())
        return tag


    async def delete_tag(self, tag_name: str):
        stmt = select(Tag).where(Tag.name == tag_name)
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()
        if tag:
            await self.db.delete(tag)
            await self.db.commit()
        return tag
