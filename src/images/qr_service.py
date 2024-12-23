# import qrcode
import uuid
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from src.images.image_service import ImageService


class QRService:
    def __init__(self, db: AsyncSession):
        self.image_service = ImageService(db)

    # @staticmethod
    # async def create_qr(image_url: str):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(image_url)
    #     qr.make(fit=True)
    #
    #     img = qr.make_image(fill_color="black", back_color="white")
    #     buffer = BytesIO()
    #     img.save(buffer, format="PNG")
    #     buffer.seek(0)
    #     return buffer

    @staticmethod
    async def generate_qr(self, post_id: int, original_image_url: str, image_filter: str):
        print('FUNCTION was called ------------------------------------------------------------ generate_qr')
        # edited_image_url = await self.image_service.check_get_edited_image(post_id, image_filter)
        # if edited_image_url:
        #     return await self.create_qr(edited_image_url)
        #
        # # Generate a new filtered image and QR
        # unique_filename = uuid.uuid4().hex
        # new_image_url = await self.image_service.image_apply_filter(
        #     original_image_url, unique_filename, image_filter
        # )
        # await self.image_service.create_image(post_id, new_image_url, image_filter)
        # return await self.create_qr(new_image_url)
