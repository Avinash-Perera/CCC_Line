from datetime import datetime
from typing import Optional, List

from pydantic import Field

from bin.requests.user_requests.user_base import UserBase
from bin.response.role_response import RoleResponse


class UserResponse(UserBase):
    id: int
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    roles: List[RoleResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True