import uuid as uuid_
from pydantic import BaseModel


class RoleResponse(BaseModel):
    uuid: uuid_.UUID
    name: str


class RolePostUpdate(BaseModel):
    name: str


class NewRoleToUser(BaseModel):
    user_id: uuid_.UUID
    role_id: uuid_.UUID
