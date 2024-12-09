from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.payments.models import Payment
from src.users.models import User


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user: Mapped['User'] = relationship('User', backref='user_invoices', lazy='joined')
    subscription_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(255), nullable=False)
    invoice_amount: Mapped[float] = mapped_column(Float, nullable=False)
    invoice_fee: Mapped[float] = mapped_column(Float, nullable=False)
    payment_id: Mapped[int] = mapped_column(Integer, ForeignKey('payments.id'), nullable=True, index=True)
    payment: Mapped['Payment'] = relationship('Payment', backref='payment_invoices', lazy='joined')
    is_paid: Mapped[bool] = mapped_column(default=False)
    paid_at: Mapped[DateTime] = mapped_column('paid_at', DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
