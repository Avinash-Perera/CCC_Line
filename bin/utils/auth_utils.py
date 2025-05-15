from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from bin.config import settings
from bin.db.postgresDB import db_connection
from bin.models.pg_user_model import User
from bin.response.user_response import UserResponse

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Create a hashed password."""
    return pwd_context.hash(password)


def create_access_token(
        data: Dict[str, Any],
        roles: list[int],
        expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now
    })

    # Adding roles as a list (supports multiple roles)
    to_encode['roles'] = roles

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(db_connection)
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))  # Ensure user_id is an integer
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError) as e:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Verify the current user is active."""
    if current_user.user_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def check_user_role(
        required_roles: list[str],
        current_user: User = Depends(get_current_active_user)
) -> User:
    """Check if user has any of the required roles."""
    user_roles = [role.name for role in current_user.roles]
    if not any(role in user_roles for role in required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


def verify_token(token):
    try:
        payload_data = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )

        print(payload_data)
        return payload_data

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError:
        raise ValueError("Invalid token")



# Role-specific dependency shortcuts
async def get_admin_user(current_user: User = Depends(get_current_active_user)):
    """Verify user has admin role."""
    return await check_user_role(["admin"], current_user)


async def get_moderator_user(current_user: User = Depends(get_current_active_user)):
    """Verify user has moderator or admin role."""
    return await check_user_role(["moderator", "admin"], current_user)