from typing import Optional
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.scores.models import Score
from src.scores.schemas import ScoreCreate, ScoreUpdate

class ScoreRepository:
    """
    Repository class to manage database operations for scores.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        :param db: The database session.
        """
        self.session = db

    async def get_score_by_id(self, score_id: int):
        """
        Retrieve a score by its unique ID.

        :param score_id: The unique identifier of the score.
        :return: The Score instance if found, otherwise None.
        """
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()
        return score


    async def get_scores_by_user_id(
        self, user_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Retrieve scores associated with a specific user ID, with optional pagination.

        :param user_id: The unique identifier of the user.
        :param limit: The maximum number of scores to return.
        :param offset: The number of scores to skip.
        :return: A list of Score instances.
        """
        stmt = select(Score).where(Score.user_id == user_id).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        scores = result.scalars().all()
        return scores


    async def get_scores_by_post_id(
        self, post_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Retrieve scores associated with a specific post ID, with optional pagination.

        :param post_id: The unique identifier of the post.
        :param limit: The maximum number of scores to return.
        :param offset: The number of scores to skip.
        :return: A list of Score instances.
        """
        stmt = select(Score).where(Score.post_id == post_id)
        result = await self.session.execute(stmt)
        scores = result.scalars().all()
        return scores


    async def create_score(self, score_data: ScoreCreate, user_id: int):
        """
        Create a new score record in the database.

        :param score_data: The data for the new score.
        :param user_id: The ID of the user creating the score.
        :return: The created Score instance.
        """
        score = Score(post_id=score_data.post_id, user_id=user_id, score=score_data.score)
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        return score


    async def update_score(self, score_id: int, score_data: ScoreUpdate):
        """
        Update an existing score record.

        :param score_id: The unique identifier of the score to update.
        :param score_data: The updated score data.
        :return: The updated Score instance if found, otherwise None.
        """
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()

        if score:
            score.score = score_data.score
            await self.session.commit()
            await self.session.refresh(score)
        return score


    async def delete_score(self, score_id: int)-> Optional[Score]:
        """
        Delete a score record by its ID.

        :param score_id: The unique identifier of the score to delete.
        :return: The deleted Score instance if found, otherwise None.
        """
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()

        if score:
            await self.session.delete(score)
            await self.session.commit()
        return score


    async def get_average_score_by_post_id(self, post_id: int):
        """
        Calculate the average score for a specific post ID.

        :param post_id: The unique identifier of the post.
        :return: The average score as a float, or None if no scores exist.
        """
        stmt = select(func.avg(Score.score).label("average_score")).where(
            Score.post_id == post_id
        )
        result = await self.session.execute(stmt)
        average_score = result.scalar_one_or_none()
        return average_score


    async def score_exists(self, user_id: int, post_id: int):
        """
        Check if a score exists for a specific user and post combination.

        :param user_id: The unique identifier of the user.
        :param post_id: The unique identifier of the post.
        :return: True if the score exists, otherwise False.
        """
        stmt = select(Score).where(Score.user_id == user_id,
                                   Score.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    

    async def delete_scores_by_post_id(self, post_id: int):
        """
        Delete all scores associated with a specific post ID.

        :param post_id: The unique identifier of the post.
        """
        stmt = delete(Score).filter(Score.post_id == post_id)
        await self.session.execute(stmt)

