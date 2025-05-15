from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from bin.requests.donation_request import DonationRequest
from bin.controllers.donation_controller import donationManager

router = APIRouter(
    prefix="/ccc-line",
    tags=["Donations"]
)

@router.post("/send-donation")
async def send_donation(request:DonationRequest):
    return await donationManager.donation(request)

@router.get("/payment-page/{donation_id}", response_class=HTMLResponse)
async def payment_page(donation_id: int):
    return await donationManager.payment_page(donation_id)

@router.get("/payment_callback")
async def payment_callback(
        request: Request
):
    return await donationManager.payment_callback(request)


@router.get("/get-currency-list")
def all_currency_list():
    return donationManager.get_currency_list()

@router.get("/get-donation-types")
def get_donation_types():
    return donationManager.donation_types()

@router.get("/get-total-general-donations")
def get_total_general_donations():
    return donationManager.get_total_donations()

@router.get("/payment-success/{donation_id}", response_class=HTMLResponse)
async def payment_success(donation_id: int):
    return await donationManager.payment_success_page(donation_id)

@router.get("/payment-failed/{donation_id}", response_class=HTMLResponse)
async def payment_failed(donation_id: int):
    return await donationManager.payment_failure_page(donation_id)