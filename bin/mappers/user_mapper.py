# bin/mappers/user_mapper.py

from typing import List
from bin.models.pg_user_model import User, Role
from bin.response.user_response import UserResponse
from bin.response.role_response import RoleResponse


class UserMapper:
    @staticmethod
    def to_user_response(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_image=user.user_image,
            hashed_password=user.hashed_password,
            is_sri_lanka_citizen=user.is_sri_lanka_citizen,
            is_backend_user=user.is_backend_user,
            user_status=user.user_status,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=UserMapper.to_role_responses(user.roles)
        )

    @staticmethod
    def to_role_responses(roles: List[Role]) -> List[RoleResponse]:
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at
            ) for role in roles
        ]
