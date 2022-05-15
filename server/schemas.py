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
