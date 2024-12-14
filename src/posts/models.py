from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base

# + id: int
# + image_id: Mapped[int] = (Integer, Foreignkey)
# + image: Image Relationship
# + description: str
# + comments: list['Comment'] Relationship
# + score_result: float
# + tags: list['Tag'] Relationship
# + edited_images: list['Image'] Relationship
# + created_at: DateTime
# + updated_at: DateTime
# + user_id: int

class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id'), nullable=False)
    image: Mapped['Image'] = relationship('Image', back_populates='posts', lazy='joined')
    description: Mapped[str] = mapped_column(String, nullable=False)
    comments: Mapped[list ['Comment'] ] = relationship('Comment', back_populates='post', lazy='joined')
    score_results: Mapped[float] = mapped_column(Float, nullable=True)
    edited_images: Mapped[list ['Image']] = relationship('Image', back_populates='edited_post', lazy='joined')
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    tags: Mapped[list["Tag"]] = relationship("PostTag", secondary=post_tag, back_populates="posts")