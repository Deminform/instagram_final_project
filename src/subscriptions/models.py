from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.orders.models import Order
from src.users.models import User

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', backref='user_subscriptions', lazy='joined')
    payment_id: Mapped[int] = mapped_column(Integer, ForeignKey('payments.id'), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plans.id'), nullable=False)
    start_date: Mapped[str] = mapped_column(String(255))
    end_date: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=False)
    is_suspended: Mapped[bool] = mapped_column(default=False)
    suspended_at: Mapped[DateTime] = mapped_column('suspended_at', DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
