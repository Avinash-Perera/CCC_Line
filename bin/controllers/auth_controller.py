from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from bin.models.pg_user_model import User
from bin.requests.user_requests.user_create import UserCreate
from bin.requests.user_requests.user_login import UserLogin
from bin.requests.user_requests.user_reset_password_confirm import UserResetPasswordConfirm
from bin.requests.user_requests.user_reset_password_request import UserResetPasswordRequest
from bin.requests.user_verify_otp import UserVerifyOTP
from bin.services.db_services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService = Depends(AuthService)):
        self.auth_service = auth_service

    def register(self, user_data: UserCreate):
        try:
            user = self.auth_service.register_user(user_data)
            return user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def login(self, login_request: UserLogin):
        auth_result = self.auth_service.authenticate_user(login_request)

        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or inactive account",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_response, token_response = auth_result


        return {
            "user": user_response,
            "tokens": token_response
        }

    def verify_otp_and_activate_account(self, otp_code: str):
        if self.auth_service.verify_otp_and_activate(otp_code):
            return {"message": "Account activated successfully"}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or user ID"
        )

    def request_password_reset(self, reset_request: UserResetPasswordRequest):
        self.auth_service.initiate_password_reset(reset_request.email)
        return {"message": "If the email exists, a reset OTP has been generated"}

    def reset_password(self, reset_data: UserResetPasswordConfirm):
        if self.auth_service.reset_password(reset_data.email, reset_data.otp, reset_data.new_password):
            return {"message": "Password updated successfully"}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or email"
        )

    def read_users_me(self, current_user: User):
        return current_user

# router = APIRouter(tags=["Authentication"])
#
# def get_auth_controller(db: Session = Depends(db_connection)):
#     return AuthController(db)
#
# @router.post("/register")
# async def register(
#     user_data: UserCreate,
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.register(user_data)
#
# @router.post("/login")
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.login(form_data)
#
# @router.post("/activate-account")
# async def activate_account(
#     otp_data: UserVerifyOTP,
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.activate_account(otp_data)
#
# @router.post("/request-password-reset")
# async def request_password_reset(
#     reset_request: UserResetPasswordRequest,
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.request_password_reset(reset_request)
#
# @router.post("/reset-password")
# async def reset_password(
#     reset_data: UserResetPasswordConfirm,
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.reset_password(reset_data)
#
# @router.get("/me")
# async def read_users_me(
#     current_user: User = Depends(get_current_active_user),
#     auth_controller: AuthController = Depends(get_auth_controller)
# ):
#     return await auth_controller.read_users_me(current_user)