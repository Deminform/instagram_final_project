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
    """
    A service class for interacting with Cloudinary, including uploading images, applying filters, and retrieving URLs.
    """

    @staticmethod
    async def apply_filter(original_image_url: str, filter_name: str) -> str:
        """
        Apply a filter to an image and return the URL of the edited image.

        :param original_image_url: The URL or public ID of the original image on Cloudinary.
        :param filter_name: The name of the filter to apply.
        :return: The URL of the edited image.
        """
        edited_image_url, options = cloudinary_url(
            original_image_url,
            transformation=[
                {"width": 1080, "height": 1080, "crop": "fill"},
                FILTER_DICT.get(filter_name),
            ]
        )
        return edited_image_url

    @staticmethod
    async def get_image_urls(image_file: UploadFile, image_filter: str = None) -> dict:
        """
        Upload an image to Cloudinary, optionally apply a filter, and return URLs for the original and edited images.

        :param image_file: The image file to upload.
        :param image_filter: (Optional) The filter to apply to the image.
        :return: A dictionary containing URLs for the original and (optionally) the edited image.
        """
        links_dict = {}
        unique_filename = uuid.uuid4().hex

        try:
            original_image_url = cloudinary.uploader.upload(
                image_file.file,
                public_id=unique_filename,
                overwrite=True,
                folder=app_config.CLOUDINARY_FOLDER,
            )
            links_dict[const.ORIGINAL_IMAGE_URL] = original_image_url["public_id"]
            if image_filter:
                edited_image_url = await CloudinaryService.apply_filter(original_image_url["public_id"], image_filter)
                links_dict[const.EDITED_IMAGE_URL] = edited_image_url
            else:
                links_dict[const.EDITED_IMAGE_URL] = original_image_url["secure_url"]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.UPLOAD_IMAGE_ERROR} -//- {e}",
            )
        return links_dict

    @staticmethod
    async def get_avatar_url(avatar_file: UploadFile, username: str) -> str:
        """
        Upload an avatar image to Cloudinary and generate a URL for it.

        :param avatar_file: The avatar image file to upload.
        :param username: The username to associate with the avatar.
        :return: The URL of the uploaded avatar image.
        """
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