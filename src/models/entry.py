from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class EntryCreate(BaseModel):
    user_id: UUID
    user_agent: str = None
    refresh_token: str = None

# class Entry(BaseModel):
#     # uuid: UUID = Field(default_factory=uuid4)
#     uuid: UUID
#     user_id: UUID
#     user_agent: str = None
#     date_time: datetime = datetime.now(timezone.utc)
#     refresh_token: str = None
#     active: bool = True
