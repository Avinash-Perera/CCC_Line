from pydantic import BaseModel,EmailStr

class DonationRequest(BaseModel):
    first_name: str
    second_name: str
    email: EmailStr
    phone_number: str
    currency_id: int
    amount: float
    donation_id: int
    rider_id: int
    message: str