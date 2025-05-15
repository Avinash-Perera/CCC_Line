from typing import Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True