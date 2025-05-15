from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    is_sri_lanka_citizen: bool = False
    user_image: Optional[str] = None