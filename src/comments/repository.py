from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.comments.models import Comment
from src.comments.schema import CommentBase


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_comment(self, post_id: int, body: CommentBase, user: User) -> Comment:
        comment = Comment(comment=body.comment, post_id=post_id, user_id=user.id)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def edit_comment(self, comment_id: int, body: CommentBase, user: User) -> Comment:
        stmt = select(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment:
            comment.comment = body.comment
            comment.is_update = True
            await self.db.commit()
            await self.db.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: int, user: User) -> Comment:
        stmt = select(Comment).filter_by(id=comment_id)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment:
            await self.db.delete(comment)
            await self.db.commit()
        return comment

    async def get_comment_by_post_all(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        stmt = select(Comment).filter_by(post_id=post_id).offset(offset).limit(limit)
        comments = await self.db.execute(stmt)
        return comments.scalars().all()

    async def get_comment_by_post_user(
        self, post_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        stmt = (
            select(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == user.id)
            .offset(offset)
            .limit(limit)
        )
        comments = await self.db.execute(stmt)
        return comments.scalars().all()

    async def get_comment_by_post_author(
        self, post_id: int, user_id: int, limit: int, offset: int, user: User
    ) -> list[Comment]:
        stmt = (
            select(Comment)
            .filter(Comment.post_id == post_id, Comment.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        comments = await self.db.execute(stmt)
        return comments.scalars().all()
