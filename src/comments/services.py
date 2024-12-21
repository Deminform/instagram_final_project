from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages
from src.users.models import User
from src.comments.models import Comment
from src.comments.schema import CommentBase
from src.comments.repository import CommentRepository


class CommentServices:
    def __init__(self, db: AsyncSession):
        self.comment_repository = CommentRepository(db)

    async def add_comment(self, post_id: int, body: CommentBase, user: User) -> Comment:
        return await self.comment_repository.add_comment(post_id, body, user)

    async def edit_comment(self, comment_id: int, body: CommentBase, user: User) -> Comment:
        comment = await self.comment_repository.edit_comment(comment_id, body, user)
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
        return comment

    async def delete_comment(self, comment_id: int, user: User) -> Comment:
        comment = await self.comment_repository.delete_comment(comment_id, user)
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_COMMENT)
        return comment

    async def get_comment_by_post_all(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        comment = await self.comment_repository.get_comment_by_post_all(
            post_id, limit, offset, user
        )
        return comment

    async def get_comment_by_post_user(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        comment = await self.comment_repository.get_comment_by_post_user(
            post_id, limit, offset, user
        )
        return comment

    async def get_comment_by_post_author(
        self, post_id: int, user_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        comment = await self.comment_repository.get_comment_by_post_author(
            post_id, user_id, limit, offset, user
        )
        return comment
