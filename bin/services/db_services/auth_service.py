import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from fastapi import Depends, BackgroundTasks
from sqlalchemy.orm import Session

from bin.config import settings
from bin.db.postgresDB import db_connection
from bin.enums.user_status import UserStatus
from bin.mappers.user_mapper import UserMapper
from bin.models.pg_user_model import User, OTP, Role
from bin.requests.user_requests.user_create import UserCreate
from bin.requests.user_requests.user_login import UserLogin
from bin.response.token_reponse import TokenResponse
from bin.response.user_response import UserResponse
from bin.services.db_services.email_service import EmailService
from bin.utils.auth_utils import get_password_hash, verify_password, create_access_token, verify_token


class AuthService:
    def __init__(self,
                 background_tasks: BackgroundTasks,
                 db: Session = Depends(db_connection),
                 user_mapper: UserMapper = Depends(UserMapper),
                 email_service: EmailService = Depends(EmailService)):
        self.db = db
        self.user_mapper = user_mapper
        self.email_service = email_service
        self._background_tasks = background_tasks

    def register_user(self, user_data: UserCreate ) -> UserResponse:
        user = self.db.query(User).filter(User.email == user_data.email).first()

        if user:
            if user.user_status == UserStatus.PENDING:
                self._send_otp(user, self._background_tasks)
                return self.user_mapper.to_user_response(user)
            raise ValueError("Email already registered")

        hashed_password = get_password_hash(user_data.password) if user_data.password else None
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            user_image=user_data.user_image,
            hashed_password=hashed_password,
            is_sri_lanka_citizen=user_data.is_sri_lanka_citizen,
            is_backend_user=False,
            user_status=UserStatus.PENDING
        )

        # admin_role = self.db.query(Role).filter(Role.name == "Admin").first()
        # if admin_role:
        #     user.roles.append(admin_role)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self._send_otp(user, self._background_tasks)
        return self.user_mapper.to_user_response(user)

    def _send_otp(self, user: User, background_tasks: BackgroundTasks) -> None:
        otp_code = self._generate_otp(user.id)
        background_tasks.add_task(self.email_service.send_otp_mail, user.email, otp_code)

    def _generate_otp(self, user_id: int, otp_type: str = "activation") -> str:
        self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.otp_type == otp_type
        ).delete()

        otp_code = ''.join(random.choices(string.digits, k=6))

        otp = OTP(
            user_id=user_id,
            otp=otp_code,
            otp_type=otp_type
        )
        self.db.add(otp)
        self.db.commit()

        return otp_code


    def authenticate_user(self, login_request: UserLogin) -> Optional[Tuple[UserResponse, TokenResponse]]:
        user = self.db.query(User).filter(User.email == login_request.email).first()
        if not user or not verify_password(login_request.password, user.hashed_password):
            return None

        if user.user_status != "active":
            raise ValueError("User account is not active")

        tokens = self.generate_tokens(user)
        user_response = self.user_mapper.to_user_response(user)
        return user_response, tokens

    def generate_tokens(self, user: User) -> TokenResponse:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        common_claims = {
            "sub": str(user.id),
            "email": user.email,
            "email_verified": user.email_verified,
        }

        access_token = create_access_token(
            data=common_claims,
            roles=[role.id for role in user.roles],
            expires_delta=access_token_expires
        )

        refresh_token = create_access_token(
            data={"sub": str(user.id), "token_type": "refresh"},
            roles=[],
            expires_delta=refresh_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token

        )


    def verify_otp_and_activate(self, otp_code: str) -> Optional[User]:
        try:
            otp = self.db.query(OTP).filter(
                OTP.otp == otp_code,
                OTP.otp_type == "activation",
                OTP.generated_time > datetime.utcnow() - timedelta(minutes=15)
            ).first()

            if not otp:
                return None

            user = self.db.query(User).filter(User.id == otp.user_id).first()
            if not user:
                return None

            user.user_status = "active"
            user.email_verified = True

            self.db.delete(otp)
            self.db.commit()

            return user

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error verifying OTP: {str(e)}")



    def initiate_password_reset(self, email: str) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return False

        self.email_service.send_password_reset_mail(user.email, self._generate_otp(user.id, "password_reset"))
        return True

    def reset_password(self, email: str, otp_code: str, new_password: str) -> bool:

        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return False

        verified_otp = self._verify_otp(user.id, otp_code, "password_reset")


        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return False

        if not self._verify_otp(user.id, otp_code, "password_reset"):
            return False

        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True

    def _verify_otp(self, user_id: int, otp_code: str, otp_type: str) -> bool:
        otp = self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.otp == otp_code,
            OTP.otp_type == otp_type,
            OTP.generated_time > datetime.utcnow() - timedelta(minutes=15)
        ).first()

        if otp:
            # Optionally delete the OTP after successful verification
            self.db.delete(otp)
            self.db.commit()
            return True
        return False

    def generate_refresh_token(self, token) -> TokenResponse:
        payload = verify_token(token)

        user_id = int(payload.get("sub"))
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.user_status != "active":
            raise ValueError("User not found or inactive")

        return self.generate_tokens(user)