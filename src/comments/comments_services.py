from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
from src.posts.repository import PostRepository
from src.users.models import User
from src.comments.models import Comment
from src.comments.schema import CommentBase
from src.comments.repository import CommentRepository


class CommentService:
    """
    Service for managing comments. It contains methods for adding, editing, deleting,
    and retrieving comments, as well as for working with comments on posts.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the comment service.

        :param db: AsyncSession: The asynchronous database session instance.
        """
        self.comment_repository = CommentRepository(db)
        self.post_repository = PostRepository(db)

    async def add_comment(self, post_id: int, body: CommentBase, user: User) -> Comment:
        """
        Add a new comment to a post.

        :param post_id: int: ID of the post to which the comment is being added.
        :param body: CommentBase: The data used to create the comment, including the comment text.
        :param user: User: The user adding the comment.
        :return: Comment: The created comment.
        :raises HTTPException: If the post with the specified ID is not found.
        """
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
            )
        return await self.comment_repository.add_comment(post_id, body, user)

    async def edit_comment(self, comment_id: int, body: CommentBase, user: User) -> Comment:
        """
        Edit an existing comment.

        :param comment_id: int: ID of the comment to be edited.
        :param body: CommentBase: The new data for editing the comment.
        :param user: User: The user editing the comment.
        :return: Comment: The edited comment.
        :raises HTTPException: If the comment is not found.
        """
        comment = await self.comment_repository.edit_comment(comment_id, body, user)
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
        return comment

    async def delete_comment(self, comment_id: int) -> Comment:
        """
        Delete a comment.

        :param comment_id: int: ID of the comment to be deleted.
        :return: Comment: The deleted comment.
        :raises HTTPException: If the comment is not found.
        """
        comment = await self.comment_repository.delete_comment(comment_id)
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
        return comment

    async def get_comment_by_post_all(self, post_id: int, limit: int, offset: int) -> list[Comment]:
        """
        Retrieve all comments for a specific post.

        :param post_id: int: ID of the post for which comments need to be retrieved.
        :param limit: int: The maximum number of comments to retrieve.
        :param offset: int: The number of comments to skip.
        :return: list[Comment]: A list of comments for the specified post.
        :raises HTTPException: If no comments are found for the specified post.
        """
        comment = await self.comment_repository.get_comment_by_post_all(post_id, limit, offset)
        if len(comment) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
        return comment

    async def get_comment_by_post_user(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        """
        Retrieve all comments from a specific user on a post.

        :param post_id: int: ID of the post for which comments need to be retrieved.
        :param limit: int: The maximum number of comments to retrieve.
        :param offset: int: The number of comments to skip.
        :param user: User: The user whose comments are to be retrieved.
        :return: list[Comment]: A list of comments from the specified user on the post.
        :raises HTTPException: If no comments are found for the specified post.
        """
        comment = await self.comment_repository.get_comment_by_post_user(
            post_id, limit, offset, user
        )
        if len(comment) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND
            )
        return comment

    async def get_comment_by_post_author(
        self, post_id: int, user_id: int, limit: int, offset: int
    ) -> list[Comment]:
        """
        Retrieve all comments from a specific author on a post.

        :param post_id: int: ID of the post for which comments need to be retrieved.
        :param user_id: int: ID of the user whose comments are to be retrieved.
        :param limit: int: The maximum number of comments to retrieve.
        :param offset: int: The number of comments to skip.
        :return: list[Comment]: A list of comments from the specified user on the post.
        :raises HTTPException: If no comments are found for the specified post.
        """
        comment = await self.comment_repository.get_comment_by_post_author(
            post_id, user_id, limit, offset
        )
        if len(comment) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return comment
