from typing import List, Optional

from pydantic import constr, Field

from bin.requests.user_requests.user_base import UserBase


class UserCreate(UserBase):
    password: Optional[constr(min_length=8, max_length=100)] = None
