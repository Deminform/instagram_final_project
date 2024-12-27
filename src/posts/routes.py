from fastapi import (
    Query,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)

from fastapi import Depends, APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages, const
from database.db import get_db
from src.posts.post_service import PostService
from src.posts.schemas import PostResponseSchema
from src.services.auth.auth_service import get_current_user
from src.users.models import User

router = APIRouter(prefix="/posts", tags=["posts"])
router_admin = APIRouter(prefix="/admin/posts", tags=["posts"])


@router_admin.get("/", response_model=list[PostResponseSchema])
async def get_posts(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        tag: str = Query(None, description="Search by tags, partial match, case insensitive"),
        keyword: str = Query(None, description="Search by description, partial match, case insensitive"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    return await post_service.get_posts(limit, offset, keyword, tag)

@router.get("/", response_model=list[PostResponseSchema])
async def get_posts(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        tag: str = Query(None, description="Search by tags, partial match, case insensitive"),
        keyword: str = Query(None, description="Search by description, partial match, case insensitive"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    return await post_service.get_posts(limit, offset, keyword, tag)


@router.get("/{post_id}", response_model=PostResponseSchema)
async def get_post_by_id(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.get_post_by_id(post_id)
    return post


@router.post("/", response_model=PostResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_post(
        description: str = Form(...,
            min_length=const.POST_DESCRIPTION_MIN_LENGTH,
            max_length=const.POST_DESCRIPTION_MAX_LENGTH,
            description=messages.POST_DESCRIPTION
),
        image_filter: str | None = Form(None),
        tags: str = Form(None, description=messages.TAG_DESCRIPTION),
        image: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.create_post(user, description, image_filter, tags, image)
    return post


@router.post("/{post_id}/qr", status_code=status.HTTP_201_CREATED)
async def create_qr(
        post_id: int,
        image_filter: str | None = Query(
            None, description=messages.IMAGE_FILTER_DESCRIPTION
        ),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    image_qr = await post_service.create_qr(post_id, image_filter)
    return StreamingResponse(image_qr, media_type="image/png")


@router.put("/{post_id}", response_model=PostResponseSchema)
async def edit_post(
        post_id: int,
        description: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.update_post_description(user, post_id, description)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post_service = PostService(db)
    post = await post_service.delete_post(user, post_id)
    return post
