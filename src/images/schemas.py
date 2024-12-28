from pydantic import BaseModel


class QRResponse(BaseModel):
    qr_code: str
    message: str
