from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from conf.const import COMMENT_MAX_LENGTH, COMMENT_MIN_LENGTH


class CommentBase(BaseModel):
    comment: str = Field(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentUpdateResponse(CommentResponse):
    is_update: bool = False
    updated_at: Optional[datetime]
