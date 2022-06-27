from . import models
from sqlalchemy.orm import Session


def check_user_exists(db: Session, user_id: int) -> bool:
    return bool(
        db.query(models.User).filter(models.User.telegram_id == user_id).first()
    )


def get_user_by_telegram_id(db: Session, telegram_id: int) -> models.User:
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
