from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    username = Column(String, index=True)
    register_date = Column(DateTime, index=True)

    messages = relationship("Message", backref="user")
    exerecises = relationship("Exercise", backref="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    text = Column(String, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))


class CurrencyPair(Base):
    __tablename__ = "currency_pairs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    pair = Column(String, index=True)
    exchange_rate = Column(Float, index=True)


class Exercise(Base):
    __tablename__ = "excercises"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    name = Column(String, index=True)
    reps = Column(Integer, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
