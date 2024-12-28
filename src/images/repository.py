from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.images.models import EditedImage


class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

    async def add_image(self, post_id, image_url, image_filter):
        edited_image = EditedImage(
            post_id=post_id,
            image_url=image_url,
            image_filter=image_filter,
        )

        self.session.add(edited_image)
        await self.session.commit()
        return edited_image

    async def get_image(self, post_id, image_filter):
        stmt = select(EditedImage).filter_by(post_id=post_id, image_filter=image_filter)
        edited_image = await self.session.execute(stmt)
        return edited_image.scalar_one_or_none()
