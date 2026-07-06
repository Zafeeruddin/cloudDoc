import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserContext


def _normalize_user_id(raw_user_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identity") from exc


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="x-user-id"),
    x_user_email: str | None = Header(default=None, alias="x-user-email"),
    x_user_name: str | None = Header(default=None, alias="x-user-name"),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> UserContext:
    if settings.auth_trust_headers:
        if not x_user_id or not x_user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing trusted identity headers")
        user_id = _normalize_user_id(x_user_id)
        email = x_user_email
        name = x_user_name
    else:
        user_id = _normalize_user_id(settings.dev_user_id)
        email = settings.dev_user_email
        name = settings.dev_user_name

    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id, email=email, name=name)
        db.add(user)
    else:
        user.email = email
        user.name = name
    db.commit()

    return UserContext(user_id=str(user_id), email=email, name=name)
