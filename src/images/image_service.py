import uuid
import cloudinary
from cloudinary.utils import cloudinary_url
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile

from conf.config import app_config
from conf.const import FILTER_DICT
from conf import messages, const
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
    async def get_image_urls(image_file: UploadFile, image_filter: str = None):
        links_dict = {}
        unique_filename = uuid.uuid4().hex

        try:
            original_image_url = cloudinary.uploader.upload(
                image_file.file,
                public_id=unique_filename,
                overwrite=True,
                folder=app_config.CLOUDINARY_FOLDER,
            )
            links_dict[const.ORIGINAL_IMAGE_URL] = original_image_url["secure_url"]

            if image_filter:
                edited_image_url, options = cloudinary_url(original_image_url['public_id'],
                                                           transformation=[
                                                               FILTER_DICT.get(image_filter),
                                                               FILTER_DICT.get('crop'),

                                                           ])
                links_dict[const.EDITED_IMAGE_URL] = edited_image_url
            else:
                links_dict[const.ORIGINAL_IMAGE_URL] = original_image_url["secure_url"]
                links_dict[const.EDITED_IMAGE_URL] = original_image_url["secure_url"]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.UPLOAD_IMAGE_ERROR} -//- {e}"
            )
        return links_dict

    # async def create_image(self, post_id: int, image_url: str, image_filter: str):
    #     edited_image = await self.image_repository.get_image(post_id, image_filter)
    #     if edited_image:
    #         return None  # Image already exists
    #
    #     result = await self.image_repository.add_image(post_id, image_url, image_filter)
    #     return result
    #
    # async def check_get_edited_image(self, post_id: int, image_filter: str):
    #     edited_image = await self.image_repository.get_image(post_id, image_filter)
    #     return edited_image.image_url if edited_image else None








