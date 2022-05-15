from .currency import (
    save_currency_rates,
    currency_exchange_message,
    exchange_advice_message,
)
from fastapi import Depends, FastAPI, HTTPException
from .extensions import redis_connect
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    redis_connect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/currency/")
async def currency(user_id: int, username: str, message_text: str, db: Session = Depends(get_db)): # TODO: указать response_model - объект нового класса, который будет формировать сообщения
    save_currency_rates(db, currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    return 'Done'


@app.get("/need_tl")
async def currency():
    """
    Считает, как выгоднее получить лиры - через рубли или через доллары на примере 100$
    100$ в лирах = 100* (15,31 -1) = 1431 tl
    100$ в рубли -> в лиры (66,76 - 3)*100/4.36=1462.12
    """
    data = get_currency_rate(currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    return exchange_advice_message(data)
