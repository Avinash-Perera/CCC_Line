from pydantic import BaseModel, Field

class UserVerifyOTP(BaseModel):
    user_id: int
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")