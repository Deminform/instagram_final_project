from sqlalchemy.ext.asyncio import AsyncSession

from src.urls.models import URLs
from src.urls.repository import URLRepository
from src.services.cloudinary_service import CloudinaryService
from src.services.qr_service import QRService


class URLService:
    """
    A service class for managing URLs, generating edited images,
    and creating QR codes for the images.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the URLService with necessary dependencies.

        :param db: The asynchronous database session.
        """
        self.image_repository = URLRepository(db)
        self.qr_service = QRService
        self.cloudinary_service = CloudinaryService

    async def create_image(self, post_id: int, image_url: str, image_filter: str):
        """
        Create and store a new image with a specific filter applied.

        :param post_id: The ID of the post associated with the image.
        :param image_url: The URL of the original image.
        :param image_filter: The filter applied to the image.
        :return: The created image record or None if it already exists.
        """
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None

        result = await self.image_repository.add_image(post_id, image_url, image_filter)
        return result

    async def check_get_edited_image(self, post_id: int, image_filter: str):
        """
        Check if an edited image with a specific filter exists for a post.

        :param post_id: The ID of the post.
        :param image_filter: The filter applied to the image.
        :return: The URL of the edited image, or None if it doesn't exist.
        """
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        return edited_image.image_url if edited_image else None

    async def generate_qr(self, post_id: int, original_image_url: str, image_filter: str):
        """
        Generate a QR code for an edited image. If the image doesn't exist,
        apply the filter and create it first.

        :param post_id: The ID of the post.
        :param original_image_url: The URL of the original image.
        :param image_filter: The filter to be applied to the image.
        :return: The generated QR code for the edited image.
        """
        edited_image_url = await self.check_get_edited_image(post_id, image_filter)

        if edited_image_url:
            return await self.qr_service.create_qr(edited_image_url)

        new_image_url = await self.cloudinary_service.apply_filter(original_image_url, image_filter)

        await self.create_image(post_id, new_image_url, image_filter)

        return await self.qr_service.create_qr(new_image_url)