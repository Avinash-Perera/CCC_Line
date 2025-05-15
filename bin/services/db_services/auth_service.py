import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends
from sqlalchemy.orm import Session

from bin.config import settings
from bin.db.postgresDB import db_connection
from bin.mappers.user_mapper import UserMapper
from bin.models.pg_user_model import User, OTP, Role
from bin.requests.user_requests.user_create import UserCreate
from bin.requests.user_requests.user_login import UserLogin
from bin.response.token_reponse import TokenResponse
from bin.response.user_response import UserResponse
from bin.services.db_services.email_service import EmailService
from bin.utils.auth_utils import get_password_hash, verify_password, create_access_token


class AuthService:
    def __init__(self,
                 db: Session = Depends(db_connection),
                 user_mapper: UserMapper = Depends(UserMapper),
                 email_service: EmailService = Depends(EmailService)):
        self.db = db
        self.user_mapper = user_mapper
        self.email_service = email_service

    def register_user(self, user_data: UserCreate) -> UserResponse:
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise ValueError("Email already registered")

        hashed_password = get_password_hash(user_data.password)
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            user_image=user_data.user_image,
            hashed_password=hashed_password,
            is_sri_lanka_citizen=user_data.is_sri_lanka_citizen,
            is_backend_user=False,
            user_status="pending"
        )

        # Find the Admin role by name
        admin_role = self.db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            user.roles.append(admin_role)  # Assigning the Admin role to the user

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Generate and store activation OTP
        otp_code = self._generate_otp(user.id)

        self.email_service.send_otp_mail(user.email, otp_code)

        return self.user_mapper.to_user_response(user)

    def authenticate_user(self, login_request: UserLogin) -> Optional[Tuple[UserResponse, TokenResponse]]:
        user = self.db.query(User).filter(User.email == login_request.email).first()
        if not user or not verify_password(login_request.password, user.hashed_password):
            return None

        if user.user_status != "active":
            raise ValueError("User account is not active")

        tokens = self.generate_tokens(user)
        user_response = self.user_mapper.to_user_response(user)
        return user_response, tokens

    # Example usage in AuthService
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

    def _generate_otp(self, user_id: int, otp_type: str = "activation") -> str:
        """Generate and store an OTP for a user"""
        # Delete any existing OTPs of this type for the user
        self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.otp_type == otp_type
        ).delete()

        # Generate a 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))

        # Store the OTP
        otp = OTP(
            user_id=user_id,
            otp=otp_code,
            otp_type=otp_type
        )
        self.db.add(otp)
        self.db.commit()

        return otp_code

    def verify_otp_and_activate(self, otp_code: str) -> Optional[User]:
        try:
            # Find the OTP record
            otp = self.db.query(OTP).filter(
                OTP.otp == otp_code,
                OTP.otp_type == "activation",
                OTP.generated_time > datetime.utcnow() - timedelta(minutes=15)
            ).first()

            if not otp:
                return None

            # Get the associated user
            user = self.db.query(User).filter(User.id == otp.user_id).first()
            if not user:
                return None

            # Activate the user
            user.user_status = "active"
            user.email_verified = True

            # Delete the used OTP
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

        self._generate_otp(user.id, "password_reset")
        return True

    def reset_password(self, email: str, otp_code: str, new_password: str) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return False

        if not self.verify_otp(user.id, otp_code, "password_reset"):
            return False

        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True