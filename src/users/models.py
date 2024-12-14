from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(70), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped['Post'] = relationship('Post', backref='users', lazy='joined')
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)


# # id: int
# + first_name: str
# + last_name: str
# + phone: str
# + email: str
# + username: str
# + avatar_url: str
# + role_id: int
# + password: str
# + refresh_token: str
# + created_at: DateTime
# + updated_at: DateTime
# + is_banned: bool
# + is_confirmed: bool
# + posts: list['Post'] Relationship
#

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
