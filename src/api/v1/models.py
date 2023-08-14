import uuid

from pydantic import BaseModel, Field


class UUIDMixIn(BaseModel):
    id: uuid.UUID = Field(..., alias="uuid")

    class Config:
        allow_population_by_field_name = True


class ResponseRole(UUIDMixIn):
    name: str = Field()


class RequestRole(BaseModel):
    name: str = Field()


class RequestNewRoleToUser(BaseModel):
    user_id: uuid.UUID = Field()
    role_id: uuid.UUID = Field()
