from datetime import datetime
from typing import Optional

from bin.requests.role_requests.role_base import RoleBase


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True