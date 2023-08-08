from typing import List

from pydantic import BaseModel

class UserRoleCreate(BaseModel):
    user_id: str
    role_id: str
