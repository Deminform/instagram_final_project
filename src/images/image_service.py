import uuid
import cloudinary
import cloudinary.uploader

from cloudinary.api import transformation
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
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


# async def generate_qr(image_url): #TODO MOVE TO QR SERVICE
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#
#     qr.add_data(image_url)
#     qr.make(fit=True)
#
#     img = qr.make_image(fill_color="black", back_color="white")
#
#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     buffer.seek(0)
#
#     return StreamingResponse(buffer, media_type="image/png")

class ImageService:
    def __init__(self, db: AsyncSession):
        self.image_repository = ImageRepository(db)

    @classmethod
    def image_apply_filter(cls, image_file, unique_filename, image_filter):
        try:
            transformation_filter = FILTER_DICT.get(image_filter)

            if transformation_filter:
                edited_image = cloudinary.uploader.upload(
                    image_file,
                    public_id=unique_filename,
                    overwrite=True,
                    folder=app_config.CLOUDINARY_FOLDER,
                    transformation=transformation_filter,
                )

                edited_image_url = edited_image["secure_url"]
                return edited_image_url

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.FILTER_IMAGE_ERROR
            )

    @staticmethod
    async def get_image_urls(image_file, image_filter=None):
        links_dict = {}
        unique_filename = uuid.uuid4().hex

        try:
            original_image = cloudinary.uploader.upload(
                image_file,
                public_id=unique_filename,
                overwrite=True,
                folder=app_config.CLOUDINARY_FOLDER
            )

            original_image_url = original_image["secure_url"]

            links_dict["original_image_url"] = original_image_url

            if image_filter:
                edited_image_url = await ImageService.image_apply_filter(image_file, unique_filename, image_filter)
                if edited_image_url:
                    links_dict["image_url"] = edited_image_url
                else:
                    links_dict["image_url"] = original_image_url
            else:
                links_dict["image_url"] = original_image_url

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.UPLOAD_IMAGE_ERROR)

        return links_dict

    async def create_image(self, post_id, image_url, image_filter):
        edited_image = await self.image_repository.get_image(post_id, image_filter)
        if edited_image:
            return None
        return await self.image_repository.add_image(post_id, image_url, image_filter)


    # async def create_qr(self, post_id, original_image_url, image_filter):    #TODO MOVE CHECK TO POST REPO AND
                                                                                #TODO LOGIC TO QR SERVIE
    #     image_with_filter = await self.image_repository.get_image(post_id, image_filter)
    #     if image_with_filter:
    #         image_with_filter_url = image_with_filter.image_url
    #         qr_image = await generate_qr(image_with_filter_url)
    #         return qr_image
    #     else:
    #         unique_filename = uuid.uuid4().hex
    #         try:
    #             transformation_filter = FILTER_DICT.get(image_filter)
    #
    #             if transformation_filter:
    #                 edited_image = cloudinary.uploader.upload(
    #                     original_image_url,
    #                     public_id=unique_filename,
    #                     overwrite=True,
    #                     folder=app_config.CLOUDINARY_FOLDER,
    #                     transformation=transformation_filter,
    #                 )
    #
    #                 edited_image_url = edited_image["secure_url"]
    #                 await self.image_repository.add_image(post_id, edited_image_url, image_filter)
    #                 qr_image = await generate_qr(edited_image_url)
    #
    #                 return qr_image
    #
    #         except Exception:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail=messages.UPLOAD_IMAGE_ERROR
    #             )






