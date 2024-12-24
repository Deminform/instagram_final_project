from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.scores.models import Score
from src.scores.repository import (
    get_score_by_id,
    get_scores_by_user_id,
    get_scores_by_post_id,
    create_score,
    update_score,
    delete_score,
    get_average_score_by_post_id,
)
from src.scores.schemas import ScoreCreate, ScoreUpdate


class ScoreService:
    def __init__(self, db: AsyncSession):
        """
        Initialization the Scores services.
        :param db: AsyncSession - object of the db session.
        """
        self.db = db

    async def fetch_score_by_id(self, score_id: int):
        """
        Get a Score by ID.
        :param score_id: int - ID score.
        :return: Score or HTTP 404 exception.
        """
        score = await get_score_by_id(self.db, score_id)
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Score not found"
            )
        return score

    async def fetch_scores_by_user(
        self, user_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Get the list of scores by user's ID.
        :param user_id: int - user's ID.
        :param limit: int - max result limit (10 by default).
        :param offset: int = pagination distance (0 by default).
        :return: list of scores.
        """
        return await get_scores_by_user_id(self.db, user_id, limit, offset)

    async def fetch_scores_by_post(
        self, post_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Get the list of the Score by post's ID.
        :param post_id: int - post's ID.
        :param limit: int - max result counts (10 by default).
        :param offset: int - pagination rate (0 by default).
        :return: score list.
        """
        return await get_scores_by_post_id(self.db, post_id, limit, offset)

    async def create_new_score(self, score_data: ScoreCreate, user, post):
        """
        Create a new Score.
        :param score_data: ScoreCreate - data for creating a score.
        :param user: User - the user who created the score.
        :param post: Post - the post to which the score relates.
        :return: created score.
        """
        return await create_score(self.db, score_data, user, post)

    async def update_existing_score(self, score_id: int, score_data: ScoreUpdate):
        """
        Update existing score.
        :param score_id: int - score's ID.
        :param score_data: ScoreUpdate - new data for update.
        :return: updated score or HTTP 404 exception.
        """
        return await update_score(self.db, score_id, score_data.score)

    async def delete_existing_score(self, score_id: int):
        """
        Delete existing Score.
        :param score_id: int - score's ID.
        :return: deleted score or HTTP 404 exception.
        """
        score = await self.fetch_score_by_id(score_id)
        return await delete_score(self.db, score)

    async def calculate_average_score(self, post_id: int):
        """
        Calculate average score for the post.
        :param post_id: int - post's ID.
        :return: average score or HTTP 404 exception, if there is no score.
        """
        average_score = await get_average_score_by_post_id(self.db, post_id)
        if average_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No scores available for this post",
            )
        return average_score
