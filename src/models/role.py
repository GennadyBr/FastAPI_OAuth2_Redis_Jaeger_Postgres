import uuid
from pydantic import BaseModel


class RoleResponse(BaseModel):
    uuid: uuid.UUID
    name: str
