from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    messages = relationship("Message", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    text = Column(String, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="messages")


class CurrencyPair(Base):
    __tablename__ = "currency_pairs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    pair = Column(String, unique=True, index=True)
    exchange_rate = Column(Integer, unique=True, index=True)
