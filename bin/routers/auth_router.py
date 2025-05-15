from fastapi import APIRouter, Depends
from requests import Session
from starlette import status

from bin.controllers.auth_controller import AuthController
from bin.controllers.donation_controller import donationManager
from bin.db.postgresDB import db_connection
from bin.requests.user_requests.user_create import UserCreate
from bin.requests.user_requests.user_login import UserLogin

auth_router = APIRouter(
    prefix="/ccc-line",
    tags=["Auth"]
)

@auth_router.put('/register', status_code=status.HTTP_200_OK)
def update_profile(user_data: UserCreate,
                    auth_controller: AuthController = Depends(AuthController)):
    return auth_controller.register(user_data)


@auth_router.put('/verify_otp', status_code=status.HTTP_200_OK)
def verify_otp_and_activate_account(otp_code: str,
                auth_controller: AuthController = Depends(AuthController)):
    return auth_controller.verify_otp_and_activate_account(otp_code)

@auth_router.post('/login', status_code=status.HTTP_200_OK)
def login( login_request: UserLogin,
          auth_controller: AuthController = Depends(AuthController)):
    return auth_controller.login(login_request)



