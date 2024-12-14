from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base

class Tag(Base):
    __tablename__ = '"tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    posts: Mapped[list["Post"]] = relationship("PostTag", secondary=post_tag, back_populates="tags")

class PostTag(Base):
    __tablename__ = "post_tag"
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id")),
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id")),