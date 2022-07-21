from datetime import datetime
from .currency import (
    save_currency_rates,
    exchange_advice_message,
    get_currency_rate,
    currency_exchange_message,
)
from fastapi import Depends, FastAPI, HTTPException
from .extensions import redis_connect
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from . import models, training, schemas
from .utils import check_user_exists

# TODO: move different endpoints to separate files.

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


@app.get("/start")
async def root(
    user_id: int, username: str, message_text: str, db: Session = Depends(get_db)
):
    if check_user_exists(db, user_id):
        return f"You are already registered. How can I help you?"
    new_user = models.User(
        telegram_id=user_id, username=username, register_date=datetime.today()
    )
    db.add(new_user)
    db.flush()
    db.add(
        models.Message(
            text=message_text,
            author_id=new_user.id,
        )
    )
    db.commit()
    return f"Привет!"


@app.get("/currency/")
async def currency(
    db: Session = Depends(get_db),
):  # TODO: указать response_model - объект нового класса, который будет формировать сообщения
    """
    Посчитать и сохранить в бд курс для заданных валютных пар
    """
    save_currency_rates(db, currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    data = get_currency_rate(currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    return currency_exchange_message(data)


@app.get("/need_tl")
async def currency(
    upwork_exchange_rate: float = None,
):
    """
    Считает, как выгоднее получить лиры - через рубли или через доллары на примере 100$
    100$ в лирах = 100* (15,31 -1) = 1431 tl
    100$ в рубли -> в лиры (66,76 - 3)*100/4.36=1462.12
    """
    data = get_currency_rate(
        currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"],
        upwork_exchange_rate=upwork_exchange_rate,
    )
    return exchange_advice_message(data)


@app.get("/get_all_exercises")
async def get_all_exercises(
    user_id: int,
    db: Session = Depends(get_db),
    get_list: bool = False,
):
    """
    Возвращает полный список упражнений пользователя
    """
    exercises = training.get_all_exercises(db, user_id=user_id)
    if get_list:
        return sorted([exercise.name for exercise in exercises])

    if exercises:
        return training.message_all_exerises(exercises)
    else:
        return "У вас нет запланированных упражнений"


@app.post("/create_exercise")
async def create_exercise(
    user_id: int,
    name: str,
    reps_per_day_target: int,
    db: Session = Depends(get_db),
):
    """
    Создаёт новое упражнение и сохраняет в БД название и количество повторений
    """
    training.create_exercise(
        db,
        exercise=schemas.ExerciseBase(
            name=name, reps_per_day_target=reps_per_day_target
        ),
        telegram_id=user_id,
    )
    return f"Установил название упражнения: '{name.title()}' и количество повторений в день - {reps_per_day_target}"



@app.post("/update_exercise")
async def update_exercise(
    user_id: int,
    name: str,
    reps_last_try: int = 0,
    db: Session = Depends(get_db),
):
    """
    Обновляет название и количество повторений упражнения по названию
    """
    exercise = training.get_exercise_by_name(db, name, user_id)
    updated_exercise = training.update_exercise(
        db,
        exercise=exercise,
        reps_last_try=reps_last_try,
    )
    return updated_exercise.prepare_update_exercise_message
