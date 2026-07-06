import json
import os

ALLOWED_TOKEN_PREFIX = os.getenv("ALLOWED_TOKEN_PREFIX", "docops")


def _parse_token(token: str) -> dict | None:
    # Format: Bearer docops:<user_id>:<email>:<display_name>
    parts = token.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    raw = parts[1].strip()
    token_parts = raw.split(":")
    if len(token_parts) < 4 or token_parts[0] != ALLOWED_TOKEN_PREFIX:
        return None

    return {
        "user_id": token_parts[1],
        "email": token_parts[2],
        "display_name": ":".join(token_parts[3:]),
    }


def handler(event, _context):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    auth_header = headers.get("authorization", "")
    user = _parse_token(auth_header)

    if not user:
        return {
            "isAuthorized": False,
            "context": {"reason": "invalid_token"},
        }

    requested_user_id = headers.get("x-user-id")
    if requested_user_id and requested_user_id != user["user_id"]:
        return {
            "isAuthorized": False,
            "context": {"reason": "user_mismatch"},
        }

    return {
        "isAuthorized": True,
        "context": {
            "user_id": user["user_id"],
            "user_email": user["email"],
            "user_name": user["display_name"],
        },
    }


if __name__ == "__main__":
    sample = {
        "headers": {
            "authorization": "Bearer docops:demo-user:demo@example.com:Demo User",
            "x-user-id": "demo-user",
        }
    }
    print(json.dumps(handler(sample, None), indent=2))
