from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.scores.models import Score
from src.scores.schemas import ScoreCreate, ScoreUpdate

class ScoreRepository:

    def __init__(self, db: AsyncSession):
        self.session = db

    async def get_score_by_id(self, score_id: int):
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()
        return score


    async def get_scores_by_user_id(
        self, user_id: int, limit: int = 10, offset: int = 0
    ):
        stmt = select(Score).where(Score.user_id == user_id).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        scores = result.scalars().all()
        return scores


    async def get_scores_by_post_id(
        self, post_id: int
    ):
        stmt = select(Score).where(Score.post_id == post_id)
        result = await self.session.execute(stmt)
        scores = result.scalars().all()
        return scores


    async def create_score(self, score_data: ScoreCreate):
        score = Score(post_id=score_data.post.id, user_id=score_data.user.id, score=score_data.score)
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        return score


    async def update_score(self, score_id: int, score_data: ScoreUpdate):
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()

        if score:
            score.score = score_data.score
            await self.session.commit()
            await self.session.refresh(score)
        return score


    async def delete_score(self, score_id: int)-> Optional[Score]:
        stmt = select(Score).where(Score.id == score_id)
        result = await self.session.execute(stmt)
        score = result.scalar_one_or_none()

        if score:
            await self.session.delete(score)
            await self.session.commit()
        return score


    async def get_average_score_by_post_id(self, post_id: int):
        stmt = select(func.avg(Score.score).label("average_score")).where(
            Score.post_id == post_id
        )
        result = await self.session.execute(stmt)
        average_score = result.scalar_one_or_none()
        return average_score


    async def score_exists(self, user_id: int, post_id: int):
        stmt = select(Score).where(Score.user_id == user_id,
                                   Score.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
