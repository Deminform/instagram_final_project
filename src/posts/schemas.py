from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.tags.schemas import TagResponseSchema


class PostSchema(BaseModel):
    description: str = Field(min_length=5, max_length=500)
    image_filter: str | None

class PostUpdateRequest(BaseModel):
    description: str

class PostResponseSchema(BaseModel):
    id: int
    image_url: str
    tags: list[TagResponseSchema] | None
    description: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
