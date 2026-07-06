from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import User

settings = get_settings()


def get_current_user(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
) -> User:
    user_id = x_user_id or settings.default_user_id
    email = x_user_email or settings.default_user_email

    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        return user

    user = User(id=user_id, email=email, display_name=user_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
