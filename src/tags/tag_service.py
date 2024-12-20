from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.repository import TagRepository


class TagService:
    def __init__(self, db: AsyncSession):
        self.tag_repository = TagRepository(db)

    async def create_tags(self, post_id: int, tags: set[str]):
        ...

    async def get_or_create_tags(self, db: AsyncSession, tags: set[str]):
        tags_list = await self.tag_repository.get_tags_by_names(db, tags)
        existing_tag_names = {tag.name for tag in tags_list}
        not_existing_tag_names = [tag for tag in tags if tag not in existing_tag_names]
        for tag in not_existing_tag_names:
            tag_obj = await self.tag_repository.create_tag(db, tag)
            tags_list.add(tag_obj)
        return tags_list
