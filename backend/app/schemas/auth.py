from pydantic import BaseModel


class UserContext(BaseModel):
    user_id: str
    email: str
    name: str | None = None
