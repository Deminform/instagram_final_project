from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base


class URLs(Base):
    __tablename__ = "edited_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)
    image_filter: Mapped[str] = mapped_column(String(100), nullable=False)
