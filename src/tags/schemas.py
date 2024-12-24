from pydantic import BaseModel, ConfigDict

from src.tags.models import Tag


class TagSchema(BaseModel):
    name: str


class TagResponseSchema(TagSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)
