from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.plans.models import Plan
from src.users.models import User

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user: Mapped['User'] = relationship('User', backref='user_subscriptions', lazy='joined')
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey('invoices.id'), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plans.id'), nullable=False, index=True)
    plan: Mapped['Plan'] = relationship('Plan', backref='plan_subscriptions', lazy='joined')
    start_date: Mapped[DateTime] = mapped_column('start_date', DateTime, nullable=True)
    end_date: Mapped[DateTime] = mapped_column('end_date', DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_suspended: Mapped[bool] = mapped_column(default=False)
    suspended_at: Mapped[DateTime] = mapped_column('suspended_at', DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
