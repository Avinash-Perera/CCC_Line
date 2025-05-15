from pydantic import BaseModel, EmailStr


class UserResetPasswordRequest(BaseModel):
    email: EmailStr