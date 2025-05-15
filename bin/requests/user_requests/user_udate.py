from typing import Optional, List

from pydantic import constr

from bin.requests.user_requests.user_base import UserBase


class UserUpdate(UserBase):
    password: Optional[constr(min_length=8, max_length=100)] = None
    role_ids: Optional[List[int]] = None