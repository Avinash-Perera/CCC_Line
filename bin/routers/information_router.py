from fastapi import APIRouter
from bin.requests.infomation_request import InfoRequest
from bin.services.email_service import send_email


router = APIRouter(
    prefix="/ccc-line",
    tags=["Info"]
)

@router.post("/get-in-touch")
def get_in_touch(request:InfoRequest):
    return send_email(request)

