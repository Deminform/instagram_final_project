from fastapi import File, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages, const
from src.images.image_service import ImageService
from src.images.qr_service import QRService
from src.posts.repository import PostRepository
from src.tags.tag_service import TagService
from src.users.models import User


class PostService:
    def __init__(self, db: AsyncSession):
        self.image_service = ImageService(db)
        self.qr_service = QRService
        self.tag_service = TagService(db)
        self.post_repository = PostRepository(db)


    async def _get_post_or_exception(self, post_id: int, user: User):
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.POST_NOT_FOUND,
            )
        if post.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.FORBIDDEN,
            )
        return post

    @staticmethod
    async def check_and_format_tag(tags: str):
        tags_set = set(tags.replace(' ', '').split(','))
        if len(tags_set) > 5:
            raise ValueError("The maximum number of tags (5) ")

        for tag in tags_set:
            if not tag or len(tag) > 30:
                raise ValueError(
                    f"Invalid tag: {tag}. Each tag must not be empty and must contain between 1 and 30 characters"
                )
        return tags_set

    async def create_post(self, user: User, description: str, image_filter: str, tags: str, image: File):
        image_urls = await self.image_service.get_image_urls(image, image_filter)
        tags = await self.check_and_format_tag(tags)

        try:
            tags = await self.tag_service.get_or_create_tags(tags)
            post = await self.post_repository.create_post(user, description, tags, image_urls)

            # if image_urls[const.EDITED_IMAGE_URL] != image_urls[const.ORIGINAL_IMAGE_URL]:
            #     await self.image_service.create_image(post.id, post.image_url, image_filter)

        except IntegrityError as e:
            await self.post_repository.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.DATA_INTEGRITY_ERROR}. -//- {e}",
            )
        return post


    async def get_post_by_id(self, post_id: int):
        return await self.post_repository.get_post_by_id(post_id)


    async def get_posts(self, limit: int, offset: int, keyword: str, tag: str):
        return await self.post_repository.get_posts(limit, offset, keyword, tag)


    async def update_post_description(self, user, post_id: int, description: str):
        post = await self._get_post_or_exception(post_id, user)
        return await self.post_repository.update_post_description(post, description)


    async def delete_post(self, user: User, post_id: int):
        post = await self._get_post_or_exception(post_id, user)
        return await self.post_repository.delete_post(post)


    async def create_qr(self, post_id: int, image_filter: str):
        post = await self.post_repository.get_post_by_id(post_id)
        # return await self.qr_service(post.id, post.original_image_url, image_filter)
