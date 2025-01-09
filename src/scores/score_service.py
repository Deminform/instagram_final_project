from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from conf import messages
from src.scores.repository import ScoreRepository
from src.scores.schemas import ScoreCreate, ScoreUpdate
from src.posts.repository import PostRepository
from src.users.models import User


class ScoreService:
    def __init__(self, db: AsyncSession):
        """
        Initialize the ScoreService with a database session.

        :param db: AsyncSession - The database session object.
        """
        self.score_repository = ScoreRepository(db)
        self.post_repository = PostRepository(db)



    async def fetch_score_by_id(self, score_id: int):
        """
        Retrieve a score by its unique ID.

        :param score_id: int - The unique identifier of the score.
        :return: The Score instance if found.
        :raises HTTPException: If the score is not found (404).
        """
        score = await self.score_repository.get_score_by_id(score_id)
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.SCORE_WARNING_NOT_FOUND
            )
        return score

    async def fetch_scores_by_user(
        self, user_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Retrieve a list of scores for a specific user.

        :param user_id: int - The unique identifier of the user.
        :param limit: int - The maximum number of scores to retrieve (default: 10).
        :param offset: int - The number of scores to skip (default: 0).
        :return: A list of Score instances.
        """
        return await self.score_repository.get_scores_by_user_id(user_id, limit, offset)

    async def fetch_scores_by_post(
        self, post_id: int, limit: int = 10, offset: int = 0
    ):
        """
        Retrieve a list of scores associated with a specific post.

        :param post_id: int - The unique identifier of the post.
        :param limit: int - The maximum number of scores to retrieve (default: 10).
        :param offset: int - The number of scores to skip (default: 0).
        :return: A list of Score instances.
        """
        return await self.score_repository.get_scores_by_post_id(post_id, limit, offset)

    async def create_new_score(self, score_data: ScoreCreate, user: User):
        """
        Create a new score for a specific post.

        :param score_data: ScoreCreate - The data required to create a new score.
        :param user: User - The user creating the score.
        :return: The created Score instance.
        :raises HTTPException: If the user has already scored the post (400),
                               or if the user is trying to score their own post (403).
        """

        if await self.score_repository.score_exists(user.id, score_data.post_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.SCORE_WARNING_ALREADY_SCORED
            )
        
        post = await self.post_repository.get_post_by_id(score_data.post_id)
        if post.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.SCORE_WARNING_SELF_SCORE
            )
        return await self.score_repository.create_score(score_data, user.id)
    
    async def update_existing_score(self, score_id: int, score_data: ScoreUpdate):
        """
        Update an existing score.

        :param score_id: int - The unique identifier of the score to update.
        :param score_data: ScoreUpdate - The updated data for the score.
        :return: The updated Score instance.
        :raises HTTPException: If the score is not found (404).
        """
        return await self.score_repository.update_score(score_id, score_data)

    async def delete_existing_score(self, score_id: int):
        """
        Delete an existing score by its ID.

        :param score_id: int - The unique identifier of the score to delete.
        :return: The deleted Score instance.
        :raises HTTPException: If the score is not found (404).
        """
        score = await self.fetch_score_by_id(score_id)
        return await self.score_repository.delete_score(score)

    async def calculate_average_score(self, post_id: int):
        """
        Calculate the average score for a specific post.

        :param post_id: int - The unique identifier of the post.
        :return: The average score as a float.
        :raises HTTPException: If there are no scores for the post (404).
        """
        average_score = await self.score_repository.get_average_score_by_post_id(post_id)
        if average_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.SCORE_WARNING_NO_SCORES,
            )
        return average_score
