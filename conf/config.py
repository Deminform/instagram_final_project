from pathlib import Path

from pydantic import ConfigDict, EmailStr, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Settings(BaseSettings):

    # Database settings -----------------------------------------------------------------------------
    DATABASE_USER: str = "username"
    DATABASE_PASSWORD: str = "9876543210"
    DATABASE_NAME: str = "database_name"
    DATABASE_HOST: str = "localhost"

    DB_URL: str = "postgresql+asyncpg://${POSTGRES_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}/${DATABASE_NAME}"

    # DEV Database settings -----------------------------------------------------------------------------
    DEV_DB_USER: str = "insta_user"
    DEV_DB_PASSWORD: str = "654321"
    DEV_DB_NAME: str = "insta"
    DEV_DB_HOST: str = "localhost"
    DEV_DB_PORT: int = 5432

    DEV_DB_URL: str = "postgresql+asyncpg://${DEV_DB_USER}:${DEV_DB_PASSWORD}@${DEV_DB_HOST}/${DEV_DB_NAME}"

    # Database settings -----------------------------------------------------------------------------
    TEST_POSTGRES_USER: str = "<DB_USERNAME>"
    TEST_POSTGRES_PASSWORD: str = "<PASSWORD>"
    TEST_POSTGRES_DBNAME: str = "<DB_NAME>"
    TEST_POSTGRES_HOST: str = "<DB_HOST>"
    TEST_POSTGRES_PORT: int = 5432
    TEST_DB_URL: str = "postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_TEST_DB}"

    # Mail settings ----------------------------------------------------------------------------------
    MAIL_USERNAME: EmailStr = "email@example.com"
    MAIL_FROM: str = MAIL_USERNAME
    MAIL_PASSWORD: str = "9876543210"
    MAIL_SERVER: str = "mail.example.com"
    MAIL_PORT: int = 1025
    MAIL_SMTP_PORT: str = '993'
    MAIL_IMAP_PORT: str = '465'
    VERIFY_EMAIL_TOKEN_LIFETIME: int = 24  # Hours

    # JWT Key --------------------------------------------------------------------------------------
    JWT_SECRET_KEY: str = "0123a654b987c"
    ALGORITHM: str = "HS256"
    TOKEN_LIFETIME: int = 60  # Minutes
    REFRESH_TOKEN_LIFETIME: int = 7  # Days

    # Redis --------------------------------------------------------------------------------------
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    # REDIS_PASSWORD: str | None = None
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
        extra="ignore", env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8"
    )  # noqa


app_config = Settings()
