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

    @property
    def exercises_list(self):
        return [exercise.name for exercise in self.exerecises]

    @property
    def exercises_dict(self):
        return {
            exercise.name: exercise.reps_per_day_target for exercise in self.exerecises
        }


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
    created_date = Column(DateTime, index=True)
    last_updated_date = Column(DateTime)

    name = Column(String, index=True, unique=True)
    reps_per_day_target = Column(Integer, index=True, default=0)
    reps_per_day_done = Column(Integer, index=True, default=0)
    reps_last_try = Column(Integer, index=True, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    @property
    def reps_per_day_left(self):
        """
        Оставшееся количество повторений в день
        """
        return self.reps_per_day_target - self.reps_per_day_done

    @property
    def prepare_update_exercise_message(self):
        """
        Сообщение об обновлении упражнения
        """
        data = {
            "reps_per_day_left": self.reps_per_day_left,
            "message": f"Обновил *{self.name}* на *{self.reps_last_try}*\nОсталось сегодня: *{self.reps_per_day_left}*",
        }
        if self.reps_per_day_left < 0:
            data.update(
                {
                    "message": f'Обновил *"{self.name.title()}"* на *{self.reps_last_try}*\nОстановись\! Уже перевыполнил план на *{abs(self.reps_per_day_left)}*\!\nКрасава\!💪🏻'
                }
            )
        elif self.reps_per_day_left == 0:
            data.update(
                {
                    "message": f'Обновил *"{self.name.title()}"* на *{self.reps_last_try}*\nС этим упражнением - всё\!💪🏻',
                }
            )
        return data
