from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from conf.config import Base