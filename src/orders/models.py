from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.users.models import User


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    order_label: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    closed_at: Mapped[DateTime] = mapped_column('closed_at', DateTime, default=None)
    is_suspended: Mapped[bool] = mapped_column(default=False)
    is_completed: Mapped[bool] = mapped_column(default=False)
    is_canceled: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str] = mapped_column(String(255))
    link_preview_files: Mapped[str] = mapped_column(String(255))
    link_source_files: Mapped[str] = mapped_column(String(255))
    link_attached_files: Mapped[str] = mapped_column(String(255))
    order_status: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', backref='user_orders', lazy='joined')
    manager_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    manager: Mapped['User'] = relationship('User', backref='manager_orders', lazy='joined')
