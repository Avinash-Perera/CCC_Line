from pydantic import BaseModel, Field


class OTPBase(BaseModel):
    otp: str = Field(..., min_length=6, max_length=6)