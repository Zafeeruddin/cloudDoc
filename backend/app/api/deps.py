from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.services.documents import get_or_create_user


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    x_user_id: Annotated[str | None, Header()] = None,
    x_user_email: Annotated[str | None, Header()] = None,
    x_user_name: Annotated[str | None, Header()] = None,
) -> User:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-user-id header. In production this is supplied by the Lambda authorizer context.",
        )
    return get_or_create_user(db=db, external_id=x_user_id, email=x_user_email, display_name=x_user_name)
