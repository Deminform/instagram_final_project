from typing import List, Set

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.comments.models import Comment
from src.images.models import Image



class PostTag(Base):
    __tablename__ = "post_tag"
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    score_result: Mapped[float] = mapped_column(Float, nullable=True)
    images: Mapped[Set['Image']] = relationship('Image', lazy='joined')
    comments: Mapped[Set['Comment'] ] = relationship('Comment', lazy='joined')
    tags: Mapped[Set["Tag"]] = relationship("Tag", secondary=PostTag.__table__)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

