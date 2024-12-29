from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.tags.models import Tag


class PostTag(Base):
    __tablename__ = "post_tag"
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    tags: Mapped[set["Tag"]] = relationship(
        "Tag",
        secondary="post_tag",
        backref="posts",
        lazy="joined"
    )
