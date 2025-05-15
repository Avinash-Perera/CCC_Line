from pydantic import BaseModel, constr


class UserResetPasswordConfirm(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=100)