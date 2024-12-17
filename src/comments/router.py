from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from conf import messages

from src.users.models import User
from src.services.services_auth import auth_service  # services auth
import src.comments.repository as repository_comments

# from src.app_users.services_roles import access_to_route_am, access_to_route_av #role

from .schemas import CommentResponse, CommentUpdateResponse, CommentBase


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/new/{post_id}", response_model=CommentResponse)
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
    comment = await repository_comments.add_comment(post_id, body, db, current_user)
    return comment


@router.put("/edit/{comment_id}", response_model=CommentUpdateResponse)
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
    comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
    return comment


@router.delete("/delete/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    # dependencies=Depends(access_to_route_am), #need a function or role class
):
    """
    The delete_comment function deletes a comment from the database.
    The function takes in an integer representing the id of the comment to be deleted,
    and returns a dictionary containing information about that comment.

    :param comment_id: int: Specify the comment that is to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: The deleted comment
    """
    comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
    return comment


@router.get(
    "/post/all/{post_id}",
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
    user: User = Depends(auth_service.get_current_user),
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
    comments = await repository_comments.get_comment_by_post_all(post_id, limit, offset, db, user)
    return comments


@router.get(
    "/post/user/{post_id}",
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
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_comment_by_post_user function returns all comments made by a user.

    :param post_id: int: Specify the post that the comment is being created for
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for the given post
    """
    comments = await repository_comments.get_comment_by_post_user(post_id, limit, offset, db, user)
    return comments


@router.get(
    "/post/author/{post_id}/{user_id}",
    response_model=list[CommentUpdateResponse],
    # dependencies=[
    #     Depends(access_to_route_am),
    # ], # roles
)
async def get_comment_by_post_author(
    post_id: int,
    user_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_comment_by_post_author function returns all comments on a given post left by a given user.

    :param post_id: int: Specify the post that the comment is being created for
    :param user_id: int: Specifies the user who created the comment
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for the given post
    """
    comments = await repository_comments.get_comment_by_post_author(
        post_id, user_id, limit, offset, db, user
    )
    return comments
