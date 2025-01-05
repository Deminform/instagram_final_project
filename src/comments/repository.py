from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.comments.models import Comment
from src.comments.schema import CommentBase


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_comment(self, post_id: int, body: CommentBase, user: User) -> Comment:
        """
        The add_comment function creates a new comment in the database.

        :param post_id: int: Identify the post that the comment is being added to
        :param body: CommentBase: Specify the type of data that is expected to be passed in
        :param user: User: Get the user_id from the logged in user
        :return: A comment object
        """
        comment = Comment(comment=body.comment, post_id=post_id, user_id=user.id)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def edit_comment(self, comment_id: int, body: CommentBase, user: User) -> Comment:
        """
        The edit_comment function allows a user to edit their own comment.

        :param comment_id: int: Find the comment in the database
        :param body: CommentBase: Specify the type of data that is expected to be passed in
        :param user: User: Get the user_id from the logged in user
        :return: Modified comment object
        """
        stmt = select(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment:
            comment.comment = body.comment
            comment.is_update = True
            await self.db.commit()
            await self.db.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: int) -> Comment:
        """
        The delete_comment function deletes a comment from the database.

        :param comment_id: int: Find the comment in the database
        :param user: User: Get the user_id from the logged in user
        :return: Deletes comment object
        """
        stmt = select(Comment).filter_by(id=comment_id)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment:
            await self.db.delete(comment)
            await self.db.commit()
        return comment

    async def delete_comment_by_post_id(self, post_id: int) -> int:
        """
        The delete_comment function deletes a comment from the database.

        :param comment_id: int: Find the comment in the database
        """
        stmt = delete(Comment).filter(Comment.post_id == post_id)
        result = await self.db.execute(stmt)

    async def get_comment_by_post_all(self, post_id: int, limit: int, offset: int) -> list[Comment]:
        """
        The get_comment_by_post_all function returns all comments to a post from the database.

        :param post_id: int: Identifies the post for which we are looking for all comments
        :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
        :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
        :param user: User: Get the user_id from the logged in user
        :return: All comment object
        """
        stmt = select(Comment).filter_by(post_id=post_id).offset(offset).limit(limit)
        comments = await self.db.execute(stmt)
        return comments.scalars().all()

    async def get_comment_by_post_user(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        """
        The get_comment_by_post_user function returns all user comments on a post from the database.

        :param post_id: int: specifies the post for which we are looking for all comments
        :param limit (int, optional): [description]. Defaults to Query(10, ge=10, le=500).
        :param offset (int, optional): [description]. Defaults to Query(0, ge=0)
        :param user: User: gets the user_id from the logged in user
        :return: all user comment objects
        """
        stmt = (
            select(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == user.id)
            .offset(offset)
            .limit(limit)
        )
        comments = await self.db.execute(stmt)
        return comments.scalars().all()

    async def get_comment_by_post_author(
        self, post_id: int, user_id: int, limit: int, offset: int
    ) -> list[Comment]:
        """
        Retrieve all comments for a specific post made by a specific user.

        :param post_id: int: ID of the post to filter comments.
        :param user_id: int: ID of the user to filter comments.
        :param limit: int: Maximum number of comments to return.
        :param offset: int: Number of comments to skip.
        :return: List of Comment objects for the specified post and user.
        """
        stmt = (
            select(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        comments = await self.db.execute(stmt)
        return list(comments.scalars())

    async def exists_comment(self, comment: str, user_id: int) -> Comment:
        """
        The exists_comment function checks if a user comment exists.

        :param comment: int: Comment text
        :param user_id: int: Specifies the user who created the comment
        :return: If the comment exists, returns the comment.
        """
        stmt = select(Comment).filter(Comment.user_id == user_id, Comment.comment == comment)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()
        return comment
