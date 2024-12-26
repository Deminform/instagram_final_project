import uuid
import cloudinary
from cloudinary.utils import cloudinary_url
import cloudinary.uploader
from fastapi import HTTPException, status, UploadFile

from conf.config import app_config
from conf.const import FILTER_DICT
from conf import messages, const

cloudinary.config(
    cloud_name=app_config.CLOUDINARY_NAME,
    api_key=app_config.CLOUDINARY_API_KEY,
    api_secret=app_config.CLOUDINARY_API_SECRET,
    secure=True,
)


class CloudinaryService:

    @staticmethod
    async def apply_filter(original_image_url, filter_name: str):
        edited_image_url, options = cloudinary_url(
            original_image_url,
            transformation=[
                FILTER_DICT.get(filter_name),
                FILTER_DICT.get("crop"),
            ],
        )
        return edited_image_url

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
                edited_image_url = await CloudinaryService.apply_filter(original_image_url, image_filter)

                links_dict[const.EDITED_IMAGE_URL] = edited_image_url
            else:
                links_dict[const.ORIGINAL_IMAGE_URL] = original_image_url["secure_url"]
                links_dict[const.EDITED_IMAGE_URL] = original_image_url["secure_url"]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.UPLOAD_IMAGE_ERROR} -//- {e}",
            )
        return links_dict


    @staticmethod
    async def get_avatar_url(avatar_file: UploadFile, username):
        r = cloudinary.uploader.upload(
            avatar_file.file, public_id=f"Inst_project/{username}", overwrite=True
        )
        src_url = cloudinary.CloudinaryImage(
            f"Inst_project/{username}"
        ).build_url(
            width=250,
            height=250,
            crop="fill",
            version=r.get("version"),
            format=r.get("format"),
        )
        return src_url