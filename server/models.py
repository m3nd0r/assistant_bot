from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Float,
    Boolean,
    Table,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True, unique=True)
    username = Column(String, index=True)
    register_date = Column(DateTime, index=True)

    messages = relationship("Message", backref="user")
    exerecises = relationship("Exercise", backref="user")

    @property
    def exercises_list(self):
        return [exercise.name for exercise in self.exerecises]

    @property
    def exercises_dict(self):
        return {
            exercise.name: exercise.reps_per_day_target for exercise in self.exerecises
        }

    @property
    def active_exercises(self):
        return [exercise for exercise in self.exerecises if exercise.active]


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
    active = Column(Boolean, index=True, default=True)
    created_date = Column(DateTime, index=True)
    last_updated_date = Column(DateTime)

    name = Column(String, index=True)
    reps_per_day_target = Column(Integer, index=True, default=0)
    reps_per_day_done = Column(Integer, index=True, default=0)
    reps_last_try = Column(Integer, index=True, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    users = relationship("UserExercise", backref="exercises")

    @property
    def reps_per_day_left(self):
        """
        Оставшееся количество повторений в день.
        Если сегодня ничего не делалось - возвращает количество повторений в день.
        """
        if (
            self.last_updated_date
            and self.last_updated_date.date() == datetime.now().date()
        ):
            return self.reps_per_day_target - self.reps_per_day_done
        else:
            return self.reps_per_day_target

    @property
    def prepare_update_exercise_message(self):
        """
        Сообщение об обновлении упражнения
        """
        data = {
            "reps_per_day_left": self.reps_per_day_left,
            "message": f"Обновил <b>{self.name}</b> на <b>{self.reps_last_try}</b>\nОсталось сегодня: <b>{self.reps_per_day_left}</b>",
        }
        if self.reps_per_day_left < 0:
            data.update(
                {
                    "message": f'Обновил <b>>"{self.name.title()}"</b> на <b>{self.reps_last_try}</b>\nОстановись\! Уже перевыполнил план на <b>{abs(self.reps_per_day_left)}</b>\!\nКрасава\!💪🏻'
                }
            )
        elif self.reps_per_day_left == 0:
            data.update(
                {
                    "message": f'Обновил <b>"{self.name.title()}"</b> на <b>{self.reps_last_try}</b>\nС этим упражнением - всё\!💪🏻',
                }
            )
        return data


class UserExercise(Base):
    __tablename__ = "user_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("excercises.id"))

    reps = Column(Integer, index=True, default=0)
    datetime = Column(DateTime, index=True)
