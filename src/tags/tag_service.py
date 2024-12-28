from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
from src.tags.repository import TagRepository


class TagService:
    def __init__(self, db: AsyncSession):
        self.tag_repository = TagRepository(db)


    async def delete_tag_by_name(self, tag):
        tag = await self.tag_repository.delete_tag(tag.lower())
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.POST_NOT_FOUND,
            )


    async def get_or_create_tags(self, tags: set[str]):
        tags_list = await self.tag_repository.get_tags_by_names(tags)
        existing_tag_names = {tag.name for tag in tags_list}
        not_existing_tag_names = [tag for tag in tags if tag not in existing_tag_names]

        try:
            new_tags = set()
            for tag in not_existing_tag_names:
                tag_obj = await self.tag_repository.create_tag(tag)
                new_tags.add(tag_obj)
            await self.tag_repository.session.commit()
            for tag in new_tags:
                await self.tag_repository.session.refresh(tag)
            tags_list.update(new_tags)
        except Exception as e:
            await self.tag_repository.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.DATA_INTEGRITY_ERROR}. -//- {e}",
            )
        return tags_list


    @staticmethod
    async def check_and_format_tag(tags: str):
        error_list = []
        tags_set = {tag.lower().strip() for tag in tags.split(",") if tag.strip()}

        if len(tags_set) > 5:
            error_list.append(messages.TAG_NUMBER_LIMIT)

        if any(len(tag) > 30 for tag in tags_set):
            error_list.append(messages.TAG_NAME_LIMIT)

        if error_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_list
            )
        return tags_set

