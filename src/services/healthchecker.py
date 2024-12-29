from fastapi import APIRouter, Depends, HTTPException, status
import redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
from conf.config import app_config
from database.db import get_db

router = APIRouter(prefix="/healthchecker", tags=["healthchecker"])


@router.get("/")
async def healthchecker(session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.DATABASE_IS_NOT_AVAILABLE,
            )
        return {"message": messages.DATABASE_IS_HEALTHY}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


#
# @router.get("/redis-status")
# async def redis_status():
#     redis_client = redis.Redis.from_url(app_config.REDIS_URL, decode_responses=True)
#     try:
#         redis_client.ping()
#         return {"message": "Redis connected!"}
#     except Exception as err:
#         raise HTTPException(status_code=500, detail=f"Redis connection error: {err}")
