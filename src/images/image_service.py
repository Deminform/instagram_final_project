from sqlalchemy.ext.asyncio import AsyncSession

from src.images.repository import ImageRepository



class ImageService:
    def __init__(self, db: AsyncSession):
        self.image_repository = ImageRepository(db)

    async def create_image(self, post_id: int, image_url: str, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None

        result = await self.image_repository.add_image(post_id, image_url, image_filter)
        return result

    async def check_get_edited_image(self, post_id: int, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        return edited_image.image_url if edited_image else None
