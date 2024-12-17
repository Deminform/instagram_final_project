from pathlib import Path

from fastapi import (
    HTTPException,
    Depends,
    status,
    APIRouter,
    Security,
    BackgroundTasks,
    Request,
    Form,
    Query,
)

import cloudinary
import cloudinary.uploader
from fastapi import Depends, APIRouter, UploadFile, File, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi_limiter.depends import RateLimiter
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from src.posts.schemas import PostResponseSchema

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponseSchema], status_code=status.HTTP_200_OK)
async def get_post_by_filter(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        user_id: int | None = Query(None, description="Get posts by user id"),
        # credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
        db: AsyncSession = Depends(get_db)):
    ...

        # - get_post_by_filter()
        # - get_post_by_id()
        # - get_post_by_user_id() - ADMIN + MODER
        # - create_post()
        # - delete_post()
        # - edit_post()
