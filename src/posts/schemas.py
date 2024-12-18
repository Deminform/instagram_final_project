from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

from conf import const


class PostSchema(BaseModel):
    user_id: int = Field(...)
    description: str = Field(min_length=5, max_length=500)
    effect: str | None
    tags: set[str] = Field(description="5 tags max")
    @field_validator("tags")
    def validate_tags(cls, tags):
        if len(tags) > 5:
            raise ValueError("The maximum number of tags (5) ")

        for tag in tags:
            if not tag or len(tag) > 30:
                raise ValueError(f"Invalid tag: {tag}. Each tag must not be empty and must contain between 1 and 30 characters")
        return tags


class PostUpdateSchema(BaseModel):
    description: str | None = Field(min_length=const.COMMENT_MIN_LENGTH, max_length=const.POST_DESCRIPTION_MAX_LENGTH)
    comment: str | None = Field(min_length=const.COMMENT_MIN_LENGTH, max_length=const.COMMENT_MAX_LENGTH)
    score: int | None = Field(ge=const.SCORE_MIN_VALUE, le=const.SCORE_MAX_VALUE)
    tags: set[str] | None = Field(description="5 tags max")
    @field_validator("tags")
    def validate_tags(cls, tags):
        if len(tags) > 5:
            raise ValueError("The maximum number of tags (5) ")


class PostResponseSchema(BaseModel):
    id: int
    images: list[str]
    tags: set[str]
    score_result: float
    description: str
    user_id: int
    created_at: str
    updated_at: str
