from sqlalchemy.ext.asyncio import AsyncSession

from src.images.models import EditedImage
from src.images.repository import ImageRepository
from src.services.cloudinary_service import CloudinaryService
from src.services.qr_service import QRService


class ImageService:
    def __init__(self, db: AsyncSession):
        self.image_repository = ImageRepository(db)
        self.qr_service = QRService
        self.cloudinary_service = CloudinaryService

    async def create_image(self, post_id: int, image_url: str, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None

        result = await self.image_repository.add_image(post_id, image_url, image_filter)
        return result

    async def check_get_edited_image(self, post_id: int, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        return edited_image.image_url if edited_image else None


    async def generate_qr(self, post_id: int, original_image_url: str, image_filter: str):
        edited_image_url = await self.check_get_edited_image(post_id, image_filter)

        if edited_image_url:
            return await self.qr_service.create_qr(edited_image_url)

        new_image_url = await self.cloudinary_service.apply_filter(original_image_url, image_filter)
        await self.create_image(post_id, new_image_url, image_filter)
        return await self.qr_service.create_qr(new_image_url)

    async def delete_urls_by_post_id(self, post_id) -> list[EditedImage]:
        # delete all URLs by post_id
        # returns a list of deleted URLs
        # NOT USED COMMIT FUNCTION (only session.delete(url))
        pass