from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import status, HTTPException, Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import ValidationError

from core.config import token_settings
from models import token as token_models
from db.token import TokenDBBase, get_token_db


async def _verify_token(token: str, token_db: TokenDBBase, type: token_models.TokenType) -> str:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        if type == token_models.TokenType.access.value:
            secret_key = token_settings.access_secret_key
            payload_model = token_models.AccessTokenPayload
        else:
            secret_key = token_settings.refresh_secret_key
            payload_model = token_models.AccessTokenPayload

        payload = jwt.decode(
            token,
            secret_key.get_secret_value(),
            algorithms=[token_settings.algorithm],
            options={"verify_exp": False, },
        )

        token_data = payload_model(**payload)

        expired = await token_db.is_exist(token)
        if token_data.exp < datetime.now(timezone.utc) or expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return token


async def verify_access_token(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
                              token_db: TokenDBBase = Depends(get_token_db),
                              ) -> str:
    token = authorization.credentials if authorization is not None else None
    token = await _verify_token(token, token_db, token_models.TokenType.access.value)
    return token


async def verify_refresh_token(refresh_token: str = Cookie(None, include_in_schema=False),
                               token_db: TokenDBBase = Depends(get_token_db),
                               ) -> str:
    token = await _verify_token(refresh_token, token_db, token_models.TokenType.refresh.value)
    return token


class TokenManagerBase(ABC):
    @abstractmethod
    def generate_access_token(self) -> str:
        """Create access token"""
        pass

    @abstractmethod
    def generate_refresh_token(self) -> str:
        """Create refresh token"""
        pass

    @abstractmethod
    def get_data_from_access_token(self) -> token_models.TokenPayloadBase:
        """Get data from access token"""
        pass

    @abstractmethod
    def get_data_from_refresh_token(self) -> token_models.TokenPayloadBase:
        """Get data from refresh token"""
        pass


class TokenManager(TokenManagerBase):
    def __init__(self, token_db: TokenDBBase) -> None:
        self.token_db = token_db

    async def _generate_token(self,
                              data: Dict[str, Any],
                              expires_delta: int,
                              secret_key: str,
                              algorithm: str,
                              payload_model: token_models.TokenPayloadBase,
                              ) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)

        token_payload = payload_model(**data, exp=expires_delta)
        encoded_jwt = jwt.encode(token_payload.dict(), secret_key, algorithm)
        return encoded_jwt

    async def generate_access_token(self, data: Dict[str, Any]) -> str:
        access_token = await self._generate_token(data,
                                                  expires_delta=token_settings.access_expire,
                                                  secret_key=token_settings.access_secret_key.get_secret_value(),
                                                  algorithm=token_settings.algorithm,
                                                  payload_model=token_models.AccessTokenPayload,
                                                  )
        return access_token

    async def generate_refresh_token(self, data: Dict[str, Any]) -> str:
        refresh_token = await self._generate_token(data,
                                                   expires_delta=token_settings.refresh_expire,
                                                   secret_key=token_settings.refresh_secret_key.get_secret_value(),
                                                   algorithm=token_settings.algorithm,
                                                   payload_model=token_models.RefreshTokenPayload,
                                                   )
        return refresh_token

    async def _get_data_from_token(self,
                                   token: str,
                                   secret_key: str,
                                   algorithm: str,
                                   payload_model: token_models.TokenPayloadBase,
                                   ) -> token_models.TokenPayloadBase:
        payload = jwt.decode(
            token, secret_key, algorithms=[algorithm], options={"verify_exp": False, }
        )
        return payload_model(**payload)

    async def get_data_from_access_token(self, token: str) -> token_models.AccessTokenPayload:
        token_data = await self._get_data_from_token(token,
                                                     secret_key=token_settings.access_secret_key.get_secret_value(),
                                                     algorithm=token_settings.algorithm,
                                                     payload_model=token_models.AccessTokenPayload,
                                                     )
        return token_data

    async def get_data_from_refresh_token(self, token: str) -> token_models.RefreshTokenPayload:
        return await self._get_data_from_token(token,
                                               secret_key=token_settings.refresh_secret_key.get_secret_value(),
                                               algorithm=token_settings.algorithm,
                                               payload_model=token_models.RefreshTokenPayload,
                                               )


async def get_token_manager(token_db: TokenDBBase = Depends(get_token_db)) -> TokenManagerBase:
    return TokenManager(token_db)
