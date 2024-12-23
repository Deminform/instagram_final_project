import uuid
import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from conf.config import app_config
from conf.const import FILTER_DICT
from conf import messages
from src.images.repository import ImageRepository

cloudinary.config(
    cloud_name=app_config.CLOUDINARY_NAME,
    api_key=app_config.CLOUDINARY_API_KEY,
    api_secret=app_config.CLOUDINARY_API_SECRET,
    secure=True,
)

class ImageService:
    def __init__(self, db: AsyncSession):
        self.image_repository = ImageRepository(db)

    @staticmethod
    async def image_apply_filter(image_url: str, unique_filename: str, image_filter: str):
        try:
            transformation_filter = FILTER_DICT.get(image_filter)
            if not transformation_filter:
                return image_url  # No filter applied, return original image URL

            edited_image = cloudinary.uploader.upload(
                image_url,
                public_id=unique_filename,
                overwrite=True,
                folder=app_config.CLOUDINARY_FOLDER,
                transformation=transformation_filter,
            )
            return edited_image["secure_url"]

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.FILTER_IMAGE_ERROR,
            )

    async def get_image_urls(self, image_file, image_filter=None):
        links_dict = {}
        unique_filename = uuid.uuid4().hex

        try:
            original_image = cloudinary.uploader.upload(
                image_file,
                public_id=unique_filename,
                overwrite=True,
                folder=app_config.CLOUDINARY_FOLDER,
            )
            links_dict["original_image_url"] = original_image["secure_url"]

            if image_filter:
                edited_image_url = await self.image_apply_filter(
                    original_image["secure_url"], unique_filename, image_filter
                )
                links_dict["image_url"] = edited_image_url
            else:
                links_dict["image_url"] = original_image["secure_url"]

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.UPLOAD_IMAGE_ERROR,
            )
        return links_dict

    async def create_image(self, post_id: int, image_url: str, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None  # Image already exists
        return await self.image_repository.add_image(post_id, image_url, image_filter)

    async def check_get_edited_image(self, post_id: int, image_filter: str):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        return edited_image.image_url if edited_image else None








