from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr


class Base(AsyncAttrs, DeclarativeBase):
    pass


class SQLBase(Base):
    __abstract__ = True

    id: Mapped[int]
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class BaseModel(SQLBase):
    __abstract__ = True

    id: Mapped[int] = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
