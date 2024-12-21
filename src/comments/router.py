from fastapi import APIRouter, HTTPException, Depends, Request, status, Path, Query, Form

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from src.users.models import User
from conf import messages
from src.services.auth import auth_service
from src.comments.schema import CommentResponse, CommentUpdateResponse, CommentBase
from src.comments.services import CommentServices

# from src.app_users.services_roles import access_to_route_am, access_to_route_a

from uuid import UUID
from typing import List


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/{post_id}", response_model=CommentResponse)
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


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    # dependencies=Depends(access_to_route_am),
):
    comment_service = CommentServices(db)
    return await comment_service.delete_comment(comment_id, current_user)


@router.get(
    "/all/{post_id}",
    response_model=list[CommentUpdateResponse],
    # dependencies=[
    #     Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT)),
    #     Depends(access_to_route_am),
    # ],
)
async def get_comment_by_post_all(
    post_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.get_comment_by_post_all(post_id, limit, offset, current_user)


@router.get(
    "/user/{post_id}",
    response_model=list[CommentUpdateResponse],
    # dependencies=[
    #     Depends(RateLimiter(times=TIMES_LIMIT, seconds=SECONDS_LIMIT)),
    #     Depends(access_to_route_am),
    # ],
)
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
    "/author/{post_id}/{user_id}",
    response_model=list[CommentUpdateResponse],
    # dependencies=[
    #     Depends(access_to_route_am),
    # ],
)
async def get_comment_by_post_author(
    post_id: int,
    user_id: UUID,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    comment_service = CommentServices(db)
    return await comment_service.get_comment_by_post_author(
        post_id, user_id, limit, offset, current_user
    )
