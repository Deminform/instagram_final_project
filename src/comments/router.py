from fastapi import APIRouter, Depends, status, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from src.users.models import User
from conf import messages
from src.services.auth import auth_service
from src.comments.schema import CommentResponse, CommentUpdateResponse, CommentBase, MessageResponse
from src.comments.comments_services import CommentService

from src.users.schemas import RoleEnum
from src.services.auth.auth_service import RoleChecker


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/{post_id}", response_model=CommentResponse)
async def add_comment(
    post_id: int,
    body: CommentBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The add_comment function creates a new comment for the post with the given id.
    The body of the comment is passed in as JSON data, and must contain a &quot;body&quot; field.
    The user who created this comment will be set to current_user.

    :param post_id: int: Specify the post that the comment is being created for
    :param body: CommentBase: Pass the data from the request body to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Check if the user is logged in
    :return: A comment object, which is then serialized as json
    """
    comment_service = CommentService(db)
    return await comment_service.add_comment(post_id, body, current_user)


@router.put("/{comment_id}", response_model=CommentUpdateResponse)
async def edit_comment(
    comment_id: int,
    body: CommentBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The edit_comment function allows a user to edit their own comment.
    The function takes in the comment_id, body and db as parameters.
    It then calls the edit_comment function from repository_comments which returns an edited c
    omment object if successful or None otherwise.
    If it is unsuccessful, it raises a 404 error with detail message COMM_NOT_FOUND.

    :param comment_id: int: Identify the comment to be edited
    :param body: CommentBase: Pass the comment body to the edit_comment function
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: None, but the function expects a commentbase object
    """
    comment_service = CommentService(db)
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
    """
    The delete_comment function deletes a comment from the database.
    The function takes in an integer representing the id of the comment to be deleted,
    and returns a dictionary containing information about that comment.
    Only administrators and moderators have the right to delete comments.

    :param comment_id: int: Specify the comment that is to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: The deleted comment
    """
    comment_service = CommentService(db)
    return await comment_service.delete_comment(comment_id)


@router.get("/{post_id}", response_model=list[CommentUpdateResponse])
async def get_comment_by_post_all(
    post_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_comment_by_post_all function returns all comments of a post

    :param post_id: int: Specify the post that the comment is being created for
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for the given post
    """
    comment_service = CommentService(db)
    return await comment_service.get_comment_by_post_all(post_id, limit, offset)


@router.get("/user/{post_id}", response_model=list[CommentUpdateResponse])
async def get_comment_by_post_user(
    post_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_comment_by_post_user function returns all comments made by a user.

    :param post_id: int: Specify the post that the comment is being created for
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for this post left by the registered user
    """
    comment_service = CommentService(db)
    return await comment_service.get_comment_by_post_user(post_id, limit, offset, current_user)


@router.get(
    "/admin/{post_id}/{user_id}",
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
    """
    The get_comment_by_post_author function returns all comments on a given post left by a given user.
    Only administrators and moderators have access to this route.

    :param post_id: int: Specify the post that the comment is being created for
    :param user_id: int: Specifies the user who created the comment
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for this post, this user
    """
    comment_service = CommentService(db)
    return await comment_service.get_comment_by_post_author(post_id, user_id, limit, offset)
