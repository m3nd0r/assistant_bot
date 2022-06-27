from datetime import datetime
from sqlalchemy.orm import Session

from . import models, schemas, utils


def create_exercise(db: Session, exercise: schemas.ExerciseBase, telegram_id: int):
    """
    Создать новое упражнение
    """
    user = utils.get_user_by_telegram_id(db, telegram_id=telegram_id)
    new_exercise = models.Exercise(
        date=datetime.now(),
        name=exercise.name,
        reps=exercise.reps,
        user_id=user.id if user else None,
    )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise


def get_exercise_by_name(db: Session, name: str, user_id: int) -> models.Exercise:
    """
    Получить объекет упражнения по имени
    """
    return (
        db.query(models.Exercise)
        .filter(models.Exercise.name == name, models.Exercise.user_id == user_id)
        .first()
    )


def get_exercises_list(db: Session, user_id: int) -> list:
    """
    Получить список всех упражнений пользователя
    """
    user = utils.get_user_by_telegram_id(db, user_id)
    return db.query(models.Exercise).filter(models.Exercise.user_id == user.id).all()


def message_exerises_list(exercises_list: list) -> str:
    """
    Собрать сообщение со списком упражнений
    """
    if exercises_list:
        exercises_names = [exercise.name.title() for exercise in exercises_list]
        return "\n".join(exercises_names)


def update_exercise(db: Session, exercise: schemas.Exercise, user_id: int):
    db.query(models.Exercise).filter(models.Exercise.id == exercise.id).update(
        {
            "date": exercise.date,
            "name": exercise.name,
            "reps": exercise.reps,
            "user_id": user_id,
        }
    )
    db.commit()
    db.refresh(exercise)
    return exercise
