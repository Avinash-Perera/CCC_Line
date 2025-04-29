from fastapi import APIRouter
from bin.requests.rider_request import RiderRequest
from bin.controllers.rider_controller import riderManager

router = APIRouter(
    prefix="/ccc-line",
    tags=["Riders"]
)

@router.post("/create-new-rider")
def send_donation(request:RiderRequest):
    return riderManager.rider_registration(request)

@router.get("/get-riders-list")
def get_all_riders_list():
    return riderManager.get_all_riders()