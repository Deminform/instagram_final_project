from pathlib import Path

from pydantic import ConfigDict, EmailStr, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Settings(BaseSettings):
    # Database settings -----------------------------------------------------------------------------
    POSTGRES_USER: str = "username"
    POSTGRES_PASSWORD: str = "9876543210"
    POSTGRES_DBNAME: str = "database_name"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DB_URL: str = (
        "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DBNAME}"
    )

    # Mail settings ----------------------------------------------------------------------------------
    MAIL_USERNAME: EmailStr = "email@example.com"
    MAIL_FROM: str = MAIL_USERNAME
    MAIL_PASSWORD: str = "9876543210"
    MAIL_SERVER: str = "mail.example.com"
    MAIL_PORT: int = 1025
    # MAIL_SMTP_PORT: str = '993'
    # MAIL_IMAP_PORT: str = '465'
    VERIFY_EMAIL_TOKEN_LIFETIME: int = 24  # Hours

    # JWT Key --------------------------------------------------------------------------------------
    JWT_SECRET_KEY: str = "0123a654b987c"
    ALGORITHM: str = "HS256"
    TOKEN_LIFETIME: int = 15  # Minutes
    REFRESH_TOKEN_LIFETIME: int = 7  # Days

    # Redis --------------------------------------------------------------------------------------
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str = (
        "redis://${REDIS_USER}:${REDIS_PASSWORD}@${REDIS_DOMAIN}:${REDIS_PORT}/${REDIS_DB}"
    )

    # Cloudinary --------------------------------------------------------------------------------------
    CLOUDINARY_FOLDER: str = "first_app"
    CLOUDINARY_NAME: str = "cloud_name"
    CLOUDINARY_API_KEY: int = 123465790
    CLOUDINARY_API_SECRET: str = "secret"
    CLOUDINARY_URL: str = (
        f"cloudinary://{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}@{CLOUDINARY_NAME}"
    )

    # Temporary code --------------------------------------------------------------------------------------
    TEMP_CODE_LIFETIME: int = 15  # minutes

    BASE_DIR: Path | None = Path(__file__).parent.parent

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512.")
        return v

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )  # noqa


app_config = Settings()
