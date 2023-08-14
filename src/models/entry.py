from uuid import UUID, uuid4

from pydantic import BaseModel

class EntryCreate(BaseModel):
    user_id: UUID
    user_agent: str = None
    refresh_token: str = None