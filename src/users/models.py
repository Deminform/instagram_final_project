from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(70), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    is_vip: Mapped[bool] = mapped_column(default=False)
    is_new_client: Mapped[bool] = mapped_column(default=True)
    is_frequent_client: Mapped[bool] = mapped_column(default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(default=False)
    is_agreement_accepted: Mapped[bool] = mapped_column(default=False)
    agreement_accepted_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    @hybrid_property
    def fullname(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'

    @fullname.expression
    def fullname(cls) -> str:
        return func.concat(cls.first_name, ' ', cls.middle_name, ' ', cls.last_name)


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)


class UserSettings(Base):
    __tablename__ = 'user_settings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    language: Mapped[str] = mapped_column(String(2))
    timezone: Mapped[str] = mapped_column(String(50))
    is_news_subscribed: Mapped[bool] = mapped_column(default=False)
    is_notifications_on: Mapped[bool] = mapped_column(default=True)


class CompanyInfo(Base):
    __tablename__ = 'company_info'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    vat_number: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    billing_address: Mapped[str] = mapped_column(String(255))
    zip: Mapped[str] = mapped_column(String(255))


class ActionHistory(Base):
    __tablename__ = 'action_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    action: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
