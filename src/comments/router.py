from fastapi import APIRouter, Depends, status, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from src.users.models import User
from conf import messages
from src.services.auth import auth_service
from src.comments.schema import CommentResponse, CommentUpdateResponse, CommentBase
from src.comments.comments_services import CommentServices

from src.users.schema import RoleEnum
from src.services.auth.auth_service import RoleChecker


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse)
async def add_comment(
    post_id: int,
    body: CommentBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.add_comment(post_id, body, current_user)


@router.put("/{comment_id}", response_model=CommentUpdateResponse)
async def edit_comment(
    comment_id: int,
    body: CommentBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.edit_comment(comment_id, body, current_user)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),
    ],
)
async def delete_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.delete_comment(comment_id)


@router.get("/", response_model=list[CommentUpdateResponse])
async def get_comment_by_post_all(
    post_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.get_comment_by_post_all(post_id, limit, offset)


@router.get("/{post_id}/user", response_model=list[CommentUpdateResponse])
async def get_comment_by_post_user(
    post_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.get_comment_by_post_user(post_id, limit, offset, current_user)


@router.get(
    "/{post_id}/{user_id}/admin",
    response_model=list[CommentUpdateResponse],
    dependencies=[
        Depends(RoleChecker([RoleEnum.MODER, RoleEnum.ADMIN])),
    ],
)
async def get_comment_by_post_author(
    post_id: int,
    user_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.get_comment_by_post_author(post_id, user_id, limit, offset)
