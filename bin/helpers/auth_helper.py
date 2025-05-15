from enum import Enum
from typing import List

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
import jwt
from jwt import PyJWTError as JWTError

from bin.config import settings
from bin.services.db_services.role_service import RoleService


class Roles(str, Enum):
    ADMIN = "Admin"


class Auth(HTTPBearer):
    def __init__(self,
                 required_roles: List[Roles],
                 auto_error: bool = False
                 ) -> None:
        self.required_roles = [role.value for role in required_roles]
        super(Auth, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, role_service: RoleService = Depends(RoleService)):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials not provided"
            )

        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_role_ids  = payload.get("roles", [])

            all_roles = role_service.get_all_roles()
            role_id_to_name = {role.id: role.name for role in all_roles}

            user_role_names = [role_id_to_name[role_id] for role_id in user_role_ids if role_id in role_id_to_name]

            # Ensure the user has at least one of the required roles
            if not any(role in user_role_names for role in self.required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions. Required roles: " + ", ".join(self.required_roles)
                )

            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except HTTPException as e:
            raise e
