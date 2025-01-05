from sqlalchemy.ext.asyncio import AsyncSession

from src.urls.models import URLs
from src.urls.repository import URLRepository
from src.services.cloudinary_service import CloudinaryService
from src.services.qr_service import QRService


class URLService:
    """
    Service layer to manage URL-related operations, including image handling and QR code generation.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the URLService with necessary dependencies.

        :param db: AsyncSession instance for database interaction
        """
        self.image_repository = URLRepository(db)
        self.qr_service = QRService
        self.cloudinary_service = CloudinaryService

    async def create_image(self, post_id: int, image_url: str, image_filter: str):
        """
        Creates a new image entry in the database if it does not already exist.

        :param post_id: ID of the associated post
        :param image_url: URL of the image to store
        :param image_filter: Filter applied to the image
        :return: The newly created image entry or None if it already exists
        """
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None

        result = await self.image_repository.add_image(post_id, image_url, image_filter)
        return result

    async def check_get_edited_image(self, post_id: int, image_filter: str):
        """
        Checks if an edited image with a specific filter exists in the database.

        :param post_id: ID of the associated post
        :param image_filter: Filter applied to the image
        :return: URL of the edited image if it exists, otherwise None
        """
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        return edited_image.image_url if edited_image else None

    async def generate_qr(self, post_id: int, original_image_url: str, image_filter: str):
        """
        Generates a QR code for an image, either using an existing edited image or by creating a new one.

        :param post_id: ID of the associated post
        :param original_image_url: URL of the original image
        :param image_filter: Filter to apply to the image
        :return: URL of the generated QR code
        """
        edited_image_url = await self.check_get_edited_image(post_id, image_filter)

        if edited_image_url:
            return await self.qr_service.create_qr(edited_image_url)

        new_image_url = await self.cloudinary_service.apply_filter(original_image_url, image_filter)

        await self.create_image(post_id, new_image_url, image_filter)

        return await self.qr_service.create_qr(new_image_url)