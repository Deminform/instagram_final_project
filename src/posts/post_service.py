from fastapi import HTTPException, status, File
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.posts.repository import PostRepository

from src.posts.schemas import PostSchema
from src.tags.tag_service import TagService
from src.users.models import User


class PostService:
    def __init__(self, db: AsyncSession):
        self.image_service = ImageService(db)
        self.tag_service = TagService(db)
        self.post_repository = PostRepository(db)
        # self.tag_repository = TagRepository(db)




    async def get_posts(self, limit, offset):
        return await self.post_repository.get_posts(limit, offset)


    async def get_post_by_id(self, post_id):
        return await self.post_repository.get_post_by_id(post_id)


    async def update_post_description(self, user, post_id, description):
        return await self.post_repository.update_post_description(user, post_id, description)


    async def create_post(self, user: User, body: PostSchema, image: File):
        image_urls = await self.image_service.get_image_urls(image, filter)

        try:
            post = await self.post_repository.create_post(user, body.description, image_urls)
            await self.image_service.create_image(post.id, post.image_url)
            await self.tag_service.create_tags(post.id, body.tags)
        except IntegrityError as e:
            await self.post_repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error.",
            )
        return post

    async def delete_post(self, user, post_id):
        return await self.post_repository.delete_post(user, post_id)

