from datetime import datetime
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from . import models, schemas, utils


def create_exercise(db: Session, exercise: schemas.ExerciseBase, telegram_id: int):
    """
    Создать новое упражнение
    """
    user = utils.get_user_by_telegram_id(db, telegram_id=telegram_id)
    new_exercise = models.Exercise(
        created_date=datetime.now(),
        name=exercise.name,
        reps_per_day_target=exercise.reps_per_day_target,
        user_id=user.id if user else None,
    )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise


def update_exercise(
    db: Session, exercise: schemas.Exercise, reps_last_try: int, active: bool = True
):
    """
    Обновить данные об упражнении
    """
    current_time = datetime.now()
    db.add(
        models.UserExercise(
            user_id=exercise.user_id,
            exercise_id=exercise.id,
            reps=reps_last_try,
            datetime=current_time,
        )
    )
    db.query(models.Exercise).filter(models.Exercise.id == exercise.id).update(
        {
            "last_updated_date": current_time,
            "reps_last_try": reps_last_try,
            "reps_per_day_done": exercise.reps_per_day_done + reps_last_try,
            "active": active,
        }
    )
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise_id: int):
    """
    Удалить упражнение
    """
    db.query(models.Exercise).filter(models.Exercise.id == exercise_id).update(
        {
            "last_updated_date": datetime.now(),
            "active": False,
        }
    )
    db.commit()
    return True


def get_exercise_by_name(
    db: Session, name: str, telegram_user_id: int, active: bool = True
) -> models.Exercise:
    """
    Получить объекет упражнения по имени
    """
    user = utils.get_user_by_telegram_id(db, telegram_id=telegram_user_id)
    return (
        db.query(models.Exercise)
        .filter(
            models.Exercise.name == name,
            models.Exercise.user_id == user.id,
            models.Exercise.active == active,
        )
        .first()
    )


def get_all_exercises(db: Session, user_id: int, active: bool = True) -> list:
    """
    Получить список всех упражнений пользователя
    """
    user = utils.get_user_by_telegram_id(db, user_id)
    if active:
        return user.active_exercises
    return user.exerecises


def message_all_exerises(exercises_list: List[models.Exercise]) -> str:
    """
    Собрать сообщение со списком упражнений
    """
    exercises_names = [
        f"<b>{exercise.name.title()}</b>:\nОсталось: <b>{exercise.reps_per_day_left}</b>\nСделано: <b>{exercise.reps_per_day_done}</b>\nЦель: <b>{exercise.reps_per_day_target}</b>\n\n"
        for exercise in exercises_list
    ]
    return "".join(exercises_names)
