from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.orders.models import Order
from src.users.models import User


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    payment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    is_paid: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    payment_method: Mapped[str] = mapped_column(String(255), nullable=False)
