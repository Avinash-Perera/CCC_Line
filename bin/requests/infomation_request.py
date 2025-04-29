from pydantic import BaseModel,EmailStr

class InfoRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    msg: str