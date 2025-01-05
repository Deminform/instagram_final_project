from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth.auth_service import get_current_user
from src.users.schemas import UserResponse, RoleEnum
from src.scores.schemas import ScoreCreate, ScoreUpdate, Score, AverageScore
from database.db import get_db
from src.scores.score_service import ScoreService


router = APIRouter(prefix="/scores", tags=["scores"])


def get_score_service(db: AsyncSession = Depends(get_db)) -> ScoreService:
    """Dependency for getting ScoreService instance."""
    return ScoreService(db)

def is_admin_or_moderator(user: UserResponse):
    """
    Check if the user has admin or moderator privilages.

    :param user: UserResponse - user information including role.
    :return: True if user is admin or moderator,otherwise raise HTTPException.
    """
    if user.role_name not in {RoleEnum.ADMIN.value, RoleEnum.MODER.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return True


@router.get("/{score_id}", response_model=Score)
async def read_score(score_id: int, service: ScoreService = Depends(get_score_service)):
    return await service.fetch_score_by_id(score_id)


@router.get("/user/{user_id}", response_model=list[Score])
async def read_scores_by_user(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    service: ScoreService = Depends(get_score_service),
):
    return await service.fetch_scores_by_user(user_id, limit, offset)


@router.get("/post/{post_id}", response_model=list[Score])
async def read_scores_by_post(
    post_id: int,
    limit: int = 10,
    offset: int = 0,
    service: ScoreService = Depends(get_score_service),
):
    return await service.fetch_scores_by_post(post_id, limit, offset)


@router.post("/", response_model=Score, status_code=status.HTTP_201_CREATED)
async def create_new_score(
        score_data: ScoreCreate,
        service: ScoreService = Depends(get_score_service),
        current_user: UserResponse = Depends(get_current_user)
):
    return await service.create_new_score(score_data, current_user)


@router.put("/{score_id}", response_model=Score)
async def update_existing_score(
    score_id: int,
    score_data: ScoreUpdate,
    service: ScoreService = Depends(get_score_service),
):
    return await service.update_existing_score(score_id, score_data)


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_score(
    score_id: int, 
    current_user: UserResponse = Depends(get_current_user),
    service: ScoreService = Depends(get_score_service)
):
    is_admin_or_moderator(current_user)
    await service.delete_existing_score(score_id)
    return {"message": "Score deleted successfully"}


@router.get("/post/{post_id}/average", response_model=AverageScore)
async def get_post_average_score(
    post_id: int, service: ScoreService = Depends(get_score_service)
):
    average_score = await service.calculate_average_score(post_id)
    return AverageScore(post_id=post_id, average_score=average_score)
