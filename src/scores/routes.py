from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth.auth_service import get_current_user
from src.users.schemas import UserResponse, RoleEnum
from src.scores.schemas import ScoreCreate, ScoreUpdate, Score, AverageScore
from src.services.auth import auth_service
from src.services.auth.auth_service import RoleChecker
from src.users.models import User
from database.db import get_db
from src.scores.score_service import ScoreService


router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/user/{user_id}", response_model=list[Score])
async def read_scores_by_user(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieve a list of scores created by a specific user, with optional pagination.

    :param user_id: The unique identifier of the user.
    :param limit: The maximum number of scores to retrieve.
    :param offset: The number of scores to skip.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user.
    :return: A list of scores.
    """
    score_service = ScoreService(db)
    return await score_service.fetch_scores_by_user(user_id, limit, offset)


@router.get("/post/{post_id}", response_model=list[Score])
async def read_scores_by_post(
    post_id: int,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieve a list of scores associated with a specific post, with optional pagination.

    :param post_id: The unique identifier of the post.
    :param limit: The maximum number of scores to retrieve.
    :param offset: The number of scores to skip.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user.
    :return: A list of scores.
    """
    score_service = ScoreService(db)
    return await score_service.fetch_scores_by_post(post_id, limit, offset)


@router.post("/", response_model=Score, status_code=status.HTTP_201_CREATED)
async def create_new_score(
        score_data: ScoreCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new score for a specific post.

    :param score_data: The data for the new score.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user creating the score.
    :return: The created score.
    """
    score_service = ScoreService(db)
    return await score_service.create_new_score(score_data, current_user)


@router.put("/{score_id}", response_model=Score)
async def update_existing_score(
    score_id: int,
    score_data: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Update an existing score by its ID.

    :param score_id: The unique identifier of the score to update.
    :param score_data: The updated score data.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user.
    :return: The updated score.
    """
    score_service = ScoreService(db)
    return await score_service.update_existing_score(score_id, score_data)


@router.delete("/{score_id}", 
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),],
            )
async def delete_existing_score(
    score_id: int,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Delete a specific score by its ID.

    This operation is restricted to users with 'MODER' or 'ADMIN' roles.

    :param score_id: The unique identifier of the score to delete.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user.
    """
    score_service = ScoreService(db)
    return await score_service.delete_existing_score(score_id)


@router.get("/post/{post_id}/average", response_model=AverageScore)
async def get_post_average_score(
    post_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Calculate the average score for a specific post.

    :param post_id: The unique identifier of the post.
    :param db: Database session dependency.
    :param current_user: The currently authenticated user.
    :return: The average score for the post.
    """
    score_service = ScoreService(db)
    average_score = await score_service.calculate_average_score(post_id)
    return AverageScore(post_id=post_id, average_score=average_score)
