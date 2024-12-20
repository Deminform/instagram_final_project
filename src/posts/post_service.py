import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

import cloudinary
import cloudinary.uploader


from conf.config import app_config
from src.posts.repository import PostRepository


class PostService:
    def __init__(self, db: AsyncSession):
        self.post_repository = PostRepository(db)
        # self.score_repository = ScoreRepository(db)
        # self.comment_repository = CommentRepository(db)
        # self.tag_repository = TagRepository(db)


    async def get_posts(self, limit, offset):
        return await self.post_repository.get_posts(limit, offset)



    async def get_post_by_id(self, post_id):
        return await self.post_repository.get_post_by_id(post_id)



    async def create_post(self, body, image):
        ext = Path(image.filename).suffix.lower()
        unique_filename = uuid.uuid4().hex
        res = cloudinary.uploader.upload(
            image.file,
            public_id=unique_filename,
            overwrite=True,
            folder=app_config.CLOUDINARY_FOLDER)

        full_public_id = res.get('public_id')  # TODO для чого? public_id
        origin_url = cloudinary.CloudinaryImage(full_public_id + ext).build_url(
            width=200,
            height=200,
            crop='fill',
            version=res.get('version')
        )

        # if body.effect:
        #     edited_url = add_effect(body, origin_url)

        tags = self.tag_repository.check_tags(body.tags)
        self.tag_repository.create_tags(tags)
        post = self.post_repository.create_post(body, edited_url)
        return post


    # async def add_effect(self, body, origin_url):
    #     if body.effect:
    #         ...
    #     return None


    async def delete_post(self, user, post_id):
        ...

