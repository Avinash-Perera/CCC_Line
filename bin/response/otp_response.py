from datetime import datetime

from bin.requests.user_requests.otp_base import OTPBase


class OTPResponse(OTPBase):
    id: int
    user_id: int
    generated_time: datetime

    class Config:
        orm_mode = True