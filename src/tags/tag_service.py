from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.repository import TagRepository


class TagService:
    def __init__(self, db: AsyncSession):
        self.tag_repository = TagRepository(db)

    async def delete_tag_by_name(self, tag):
        await self.tag_repository.delete_tag(tag)

    async def get_or_create_tags(self, tags: set[str]):
        if len(tags) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum number of tags is 5",
            )
        tags_list = await self.tag_repository.get_tags_by_names(tags)
        existing_tag_names = {tag.name for tag in tags_list}
        not_existing_tag_names = [tag for tag in tags if tag not in existing_tag_names]
        for tag in not_existing_tag_names:
            tag_obj = await self.tag_repository.create_tag(tag)
            tags_list.add(tag_obj)
        return tags_list
