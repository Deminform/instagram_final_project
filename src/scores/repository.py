from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.scores.models import Score
from src.scores.schemas import ScoreCreate, ScoreUpdate
from src.posts.models import Post
from src.users.models import User


async def get_score_by_id(db: AsyncSession, score_id: int):
    stmt = select(Score).where(Score.id == score_id)
    result = await db.execute(stmt)
    score = result.scalar_one_or_none()
    return score


async def get_scores_by_user_id(db: AsyncSession, user_id: int, limit: int = 10, offset: int = 0):
    stmt = select(Score).where(Score.user_id == user_id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    scores = result.scalars().all()
    return scores


async def get_scores_by_post_id(db: AsyncSession, post_id: int, limit: int = 10, offset: int = 0):
    stmt = select(Score).where(Score.post_id == post_id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    scores = result.scalars().all()
    return scores


async def create_score(db: AsyncSession, score_data: ScoreCreate):
    score = Score(post_id=score_data.post.id, user_id=score_data.user.id, score=score_data.score)
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score


async def update_score(db: AsyncSession, score_id: int, score_data: ScoreUpdate):
    stmt = select(Score).where(Score.id == score_id)
    result = await db.execute(stmt)
    score = result.scalar_one_or_none()

    if score:
        score.score = score_data.score
        await db.commit()
        await db.refresh(score)
    return score


async def delete_score(db: AsyncSession, score_id: int):
    stmt = select(Score).where(Score.id == score_id)
    result = await db.execute(stmt)
    score = result.scalar_one_or_none()

    if score:
        await db.delete(score)
        await db.commit()
    return score


async def get_average_score_by_post_id(db: AsyncSession, post_id: int):
    stmt = select(func.avg(Score.score).label('average_score')).where(Score.post_id == post_id)
    result = await db.execute(stmt)
    average_score = result.scalar_one_or_none()
    return average_score


async def score_exists(db: AsyncSession, user_id: int, post_id: int):
    stmt = select(Score).where(Score.user_id == user_id, 
                               Score.post_id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def delete_scores_by_id(db: AsyncSession, post_id: int) -> list[Score]:
    stmt = select(Score).where(Score.post_id == post_id)
    result = await db.execute(stmt)
    scores = result.scalars().all()

    for score in scores:
        await db.delete(score)

    return scores