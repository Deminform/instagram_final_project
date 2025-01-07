from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from fastapi_mail.errors import ConnectionErrors
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, EmailStr
from starlette.datastructures import URL

from conf.config import app_config
from src.services.auth.auth_service import create_verification_token

env = Environment(loader=FileSystemLoader("src/templates"))


class EmailSchema(BaseModel):
    email: EmailStr


mail_conf = ConnectionConfig(
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
    MAIL_FROM=app_config.MAIL_FROM,
    MAIL_FROM_NAME='Insta - Final Project',
    MAIL_PORT=app_config.MAIL_IMAP_PORT,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_verification_email(email: EmailStr, host: URL):
    """
    Send an email with a verification link to the specified email address.

    This function generates a verification token and sends an email to the provided email address
    containing a verification link. The email is sent using the `FastMail` service with an HTML body.

    :param email: The email address to which the verification email will be sent.
    :type email: EmailStr
    :param host: The host URL used to generate the verification link.
    :type host: URL
    :return: None
    :raises ConnectionErrors: If there is an error during the email sending process.
    """
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
