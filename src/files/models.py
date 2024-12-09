from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.orders.models import Order
from src.users.models import User


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    file_url: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user: Mapped['User'] = relationship('User', backref='user_files', lazy='joined')
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    order: Mapped['Order'] = relationship('Order', backref='order_files', lazy='joined')
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
