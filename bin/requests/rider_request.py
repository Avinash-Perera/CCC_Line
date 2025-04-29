from pydantic import BaseModel,EmailStr

class RiderRequest(BaseModel):
    rider_name: str
    rider_email: EmailStr
    rider_phone_no: str
    rider_goal: float
    rider_raise: float
    rider_img: str