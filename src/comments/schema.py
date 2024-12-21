from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class CommentBase(BaseModel):
    comment: str = Field(min_length=3, max_length=1500)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: UUID
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentUpdateResponse(CommentResponse):
    is_update: bool = False
    updated_at: Optional[datetime]
