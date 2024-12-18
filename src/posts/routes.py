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

from conf import messages
from database.db import get_db
from src.posts.schemas import PostResponseSchema, PostSchema, PostUpdateSchema
from src.posts import repository as posts_repository
from src.users.models import User
from src.services.auth import auth_service
from src.images import repository as images_repository
from src.comments import repository as comment_repository
from src.scores import repository as score_repository

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponseSchema])
async def get_post_by_filter(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        user_id: int | None = Query(None, description="Get posts by user id"),
        db: AsyncSession = Depends(get_db)
        # user: User = Depends(auth_service.get_current_user),
):
    posts = await posts_repository.get_post_by_filter(db, user_id, limit, offset)
    return posts

@router.get("/{post_id}", response_model=PostResponseSchema)
async def get_post_by_id(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    post = await posts_repository.get_post_by_id(db, user, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    return post



@router.post("/", response_model=PostResponseSchema)
async def create_post(
        body: PostSchema,
        image: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    image = await images_repository.create_image(db, image)
    post = await posts_repository.create_post(db, user, body, image)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    post = await posts_repository.delete_post(db, user, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    return post



@router.put("/{post_id}", response_model=PostResponseSchema)
async def edit_post(
        post_id: int,
        body: PostUpdateSchema,
        image: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    post = await posts_repository.get_post_by_id(db, user, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )

    comment = comment_repository.create_comment(db, post.id, user, body.comment)
    score = score_repository.get_average_score(db, post.id, user, body.score)
    # image = images_repository.create_image(db, post.id, user, image)
    post = await posts_repository.update_post(db, post_id, body)



        # - get_post_by_filter()
        # - get_post_by_id()
        # - get_post_by_user_id() - ADMIN + MODER
        # - create_post()
        # - delete_post()
        # - edit_post()
