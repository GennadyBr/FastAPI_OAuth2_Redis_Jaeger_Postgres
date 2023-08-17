from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel


class TokenType(str, Enum):
    access = 'access'
    refresh = 'refresh'


class TokenPayloadBase(BaseModel):
    sub: str
    login: str
    role: List[str]
    exp: datetime

    @property
    def left_time(self):
        delta = datetime.now(timezone.utc) - self.exp
        return delta.seconds  # sec


class AccessTokenPayload(TokenPayloadBase):
    pass


class RefreshTokenPayload(TokenPayloadBase):
    session_id: str
