import os
from http import HTTPStatus


ALLOWED_BEARER_PREFIX = os.environ.get("ALLOWED_BEARER_PREFIX", "docops:")


def handler(event, _context):
    token = _extract_token(event)
    if not token or not token.startswith(ALLOWED_BEARER_PREFIX):
        return _deny()

    payload = token[len(ALLOWED_BEARER_PREFIX) :]
    parts = payload.split(":")
    if len(parts) < 3:
        return _deny()

    user_id, user_email, *name_parts = parts
    user_name = ":".join(name_parts).strip() or user_email

    return {
        "isAuthorized": True,
        "context": {
            "userId": user_id,
            "userEmail": user_email,
            "userName": user_name,
        },
    }


def _extract_token(event):
    headers = (event or {}).get("headers") or {}
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if not auth_header:
        return None
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


def _deny():
    return {
        "isAuthorized": False,
        "context": {
            "statusCode": str(HTTPStatus.UNAUTHORIZED.value)
        },
    }
