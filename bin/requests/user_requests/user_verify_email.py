from pydantic import BaseModel


class UserVerifyEmail(BaseModel):
    token: str