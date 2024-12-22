from pydantic import BaseModel, Field
from typing import Optional


class ScoreBase(BaseModel):
    post_id: int = Field(..., description="ID of the post associate with the score")
    user_id: int = Field(..., description="ID of the user who provided the score")
    score: int = Field(..., ge=1, le=5, description="Score value (must be between 1 and 5)")


class ScoreCreate(ScoreBase):
    """Schema for creating a new score."""

    pass


class ScoreUpdate(BaseModel):
    """Schema for updating an existing score."""

    score: int = Field(..., ge=1, le=5, description="Updated score value (must be between 1 and 5)")


class Score(ScoreBase):
    id: int = Field(..., description="Unique identifier for the score.")

    class Config:
        from_attributes = True


class AverageScore(BaseModel):
    post_id: int = Field(
        ..., description="ID of the post for which the average score is calculated."
    )
    average_score: float = Field(..., description="The average score for the post")
