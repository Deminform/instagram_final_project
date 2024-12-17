from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr, BaseModel
from jinja2 import Environment, FileSystemLoader
from starlette.datastructures import URL

from conf.config import app_config
from src.auth.utils import create_verification_token

env = Environment(loader=FileSystemLoader("src/templates"))


class EmailSchema(BaseModel):
    email: EmailStr


mail_conf = ConnectionConfig(
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
    MAIL_FROM=app_config.MAIL_FROM,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_verification_email(email: EmailStr, host: URL):
    try:
        verification_token = create_verification_token(email)
        template = env.get_template("verification_email.html")
        email_body = template.render(host=host, token=verification_token)
        message = MessageSchema(
            subject="Email verification",
            recipients=[email],
            body=email_body,
            subtype="html",
        )

        fm = FastMail(mail_conf)
        await fm.send_message(message)
    except ConnectionErrors as err:
        print(err)
