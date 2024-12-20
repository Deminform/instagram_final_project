from fastapi import (
    Query, HTTPException, status, UploadFile, File,
)

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
from database.db import get_db
from src.posts.schemas import PostResponseSchema, PostSchema
from src.users.models import User
from src.services.auth.utils import get_current_user
from src.posts.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponseSchema])
async def get_posts(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    return await post_service.get_posts(limit, offset)


@router.get("/{post_id}", response_model=PostResponseSchema)
async def get_post_by_id(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    post_service = PostService(db)
    post = await post_service.get_post_by_id(post_id)
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
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.create_post(user, body, image)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.delete_post(user, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    return post


@router.put("/{post_id}", response_model=PostResponseSchema)
async def edit_post(
        post_id: int,
        description: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.update_post_description(user, post_id, description)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
        )
    return post
