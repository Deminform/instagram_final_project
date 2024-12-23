from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    comment: Mapped[str] = mapped_column(String(300), nullable=False)
    is_update: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )

