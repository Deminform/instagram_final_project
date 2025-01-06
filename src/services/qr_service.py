import qrcode
from io import BytesIO


class QRService:
    """
    A service class for generating QR codes from image URLs.
    """

    @staticmethod
    async def create_qr(image_url: str):
        """
        Generate a QR code for the given image URL.

        Args:
            image_url (str): The URL to encode in the QR code.

        Returns:
            BytesIO: A buffer containing the QR code image in PNG format.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(image_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer