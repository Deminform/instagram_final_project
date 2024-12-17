from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Comment
from .schemas import CommentBase
from src.users.models import User


async def add_comment(post_id: int, body: CommentBase, db: AsyncSession, user: User) -> Comment:
    """
    The add_comment function creates a new comment in the database.

    :param post_id: int: Identify the post that the comment is being added to
    :param body: CommentBase: Specify the type of data that is expected to be passed in
    :param db: Session: Get the database session
    :param user: User: Get the user_id from the logged in user
    :return: A comment object
    """
    comment = Comment(comment=body.comment, post_id=post_id, user_id=user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def edit_comment(comment_id: int, body: CommentBase, db: AsyncSession, user: User) -> Comment:
    """
    The edit_comment function allows a user to edit their own comment.

    :param comment_id: int: Find the comment in the database
    :param body: CommentBase: Specify the type of data that is expected to be passed in
    :param db: Session: Get the database session
    :param user: User: Get the user_id from the logged in user
    :return: Modified comment object
    """
    stmt = select(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        comment.comment = body.comment
        comment.is_update = True
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession, user: User) -> Comment:
    """
    The delete_comment function deletes a comment from the database.

    :param comment_id: int: Find the comment in the database
    :param db: Session: Get the database session
    :param user: User: Get the user_id from the logged in user
    :return: Deletes comment object
    """
    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment


async def get_comment_by_post_all(
    post_id: int, limit: int, offset: int, db: AsyncSession, user: User
) -> list[Comment]:
    """
    The get_comment_by_post_all function returns all comments to a post from the database.

    :param post_id: int: Identifies the post for which we are looking for all comments
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param user: User: Get the user_id from the logged in user
    :return: All comment object
    """
    stmt = select(Comment).filter_by(post_id=post_id).offset(offset).limit(limit)
    comments = await db.execute(stmt)
    return comments.scalars().all()


async def get_comment_by_post_user(
    post_id: int, limit: int, offset: int, db: AsyncSession, user: User
) -> list[Comment]:
    """
    The get_comment_by_post_user function returns all user comments on a post from the database.

    :param post_id: int: Identifies the post for which we are looking for all comments
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param user: User: Get the user_id from the logged in user
    :return: All user comment object
    """
    stmt = select(Comment).filter_by(post_id=post_id, user_id=user.id).offset(offset).limit(limit)
    comments = await db.execute(stmt)
    return comments.scalars().all()


async def get_comment_by_post_author(
    post_id: int, user_id: int, limit: int, offset: int, db: AsyncSession, user: User
) -> list[Comment]:
    """
    The get_comment_by_post_author function returns all comments in the database for the specified post,
    left by the specified user.

    :param post_id: int: Specify the post that the comment is being created for
    :param user_id: int: Specifies the user who created the comment
    :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
    :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: All comment objects for the given post
    """
    stmt = select(Comment).filter_by(post_id=post_id, user_id=user_id).offset(offset).limit(limit)
    comments = await db.execute(stmt)
    return comments.scalars().all()
