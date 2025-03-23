from enum import Enum
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import UUID, Column, Integer, DateTime,  String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TShortUrl(Base):
    __tablename__ = "short_url"

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_name = Column(String, nullable=False, unique=True, index=True)
    original_url = Column(String, nullable=False, index=True)
    user_id = Column(UUID, index=True)
    create_time = Column(DateTime, nullable=False)
    modify_time = Column(DateTime, nullable=False)
    redirect_count = Column(Integer, nullable=False)
    last_redirect = Column(DateTime, index=True)
    expires_at = Column(DateTime, index=True)


class EventType(int, Enum):
    AddShort = 1,
    UpdateShort = 2,
    RemoveShort = 3,
    ShortIsExpired = 4,
    ShortIsNotUsed = 5


class TEvents(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    short_url = Column(String, nullable=False, index=True)
    event_type = Column(Integer, nullable=False, index=True)
    datetime = Column(DateTime, nullable=False, index=True)
    description = Column(String)


class TUser(SQLAlchemyBaseUserTableUUID, Base):
    pass
