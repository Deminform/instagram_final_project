from typing import Optional

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.config import Base
from src.posts.models import Post




class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(70), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    posts: Mapped['Post'] = relationship('Post', backref='users', lazy='select')
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'))
    role: Mapped["Role"] = relationship("Role", lazy="selectin")
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def role_name(self) -> Optional[str]:
        return self.role.name if self.role else None


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)


class Token(Base):
    __tablename__ = "tokens"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    access_token: Mapped[str] = mapped_column(String(450), primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(450), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())