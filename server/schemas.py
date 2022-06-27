from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    id: int
    message_id: str
    text: str
    author_id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    is_active: bool
    messages: list[Message] = []

    class Config:
        orm_mode = True


class ExerciseBase(BaseModel):
    name: str
    reps: int


class Exercise(ExerciseBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        orm_mode = True
