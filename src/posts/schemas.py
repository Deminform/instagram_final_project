from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from conf import const
from src.tags.models import Tag
from src.tags.schemas import TagResponseSchema


class PostSchema(BaseModel):
    description: str = Field(min_length=5, max_length=500)
    image_filter: str | None


class PostResponseSchema(BaseModel):
    id: int
    image_url: str
    tags: list[TagResponseSchema] | None
    description: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
