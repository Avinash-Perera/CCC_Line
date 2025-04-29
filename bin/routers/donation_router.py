from fastapi import APIRouter
from bin.requests.donation_request import DonationRequest
from bin.controllers.donation_controller import donationManager

router = APIRouter(
    prefix="/ccc-line",
    tags=["Donations"]
)

@router.post("/send-donation")
def send_donation(request:DonationRequest):
    return donationManager.donation(request)

@router.get("/get-currency-list")
def all_currency_list():
    return donationManager.get_currency_list()

@router.get("/get-donation-types")
def get_donation_types():
    return donationManager.donation_types()

@router.get("/get-total-general-donations")
def get_total_general_donations():
    return donationManager.get_total_donations()