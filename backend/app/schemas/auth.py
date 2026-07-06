from pydantic import BaseModel, EmailStr


class UserContext(BaseModel):
    user_id: str
    email: EmailStr
    name: str | None = None

