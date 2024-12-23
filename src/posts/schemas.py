from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from conf import const


class PostSchema(BaseModel):
    description: str = Field(min_length=5, max_length=500)
    image_filter: str | None
    tags: set[str] = Field(description="5 tags max")

    @field_validator("tags")
    def validate_tags(cls, tags):
        if len(tags) > 5:
            raise ValueError("The maximum number of tags (5) ")

        for tag in tags:
            if not tag or len(tag) > 30:
                raise ValueError(
                    f"Invalid tag: {tag}. Each tag must not be empty and must contain between 1 and 30 characters"
                )
        return tags


class PostResponseSchema(BaseModel):
    id: int
    image_url: str
    tags: set[str]
    score_result: float
    description: str
    user_id: int
    created_at: str
    updated_at: str
