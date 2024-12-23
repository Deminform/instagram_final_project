from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
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
