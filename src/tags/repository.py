from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import Tag


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

    async def create_tag(self, tag_name: str):
        tag = Tag(name=tag_name)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def get_tags_by_names(self, tags_list: set[str]) -> set[Tag]:
        stmt = select(Tag).where(Tag.name.in_(tags_list))
        result = await self.session.execute(stmt)
        tag = set(result.scalars().all())
        return tag

    async def delete_tag(self, tag_name: str):
        stmt = select(Tag).where(Tag.name == tag_name)
        result = await self.session.execute(stmt)
        tag = result.scalar_one_or_none()
        if tag:
            await self.session.delete(tag)
            await self.session.commit()
        return tag
