from abc import ABC, abstractmethod
import bcrypt
from typing import List, Tuple
from functools import lru_cache
import logging

from fastapi import status, HTTPException, Depends
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

import logging.config
from core.logger import LOGGING
from db.token import TokenDBBase, get_token_db
from db.models import User as DBUser, Entry as DBEntry
from models import user as user_models
from crud import user as user_dal, role as role_dal, entry as entry_dal, crud_social as user_socials_dal
from utils.token_manager import TokenManagerBase, get_token_manager
from db.session import get_db

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class HashManagerBase(ABC):
    """Hashing and verifying passwords"""

    @abstractmethod
    def hash_pwd(self, pwd: str) -> str:
        """Get a hashed password"""
        pass

    @abstractmethod
    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        """Password match check"""
        pass


class AuthServiceBase(ABC):
    """Service for user authorization"""

    @abstractmethod
    async def register(self) -> DBUser:
        """Registration of new users"""
        pass

    @abstractmethod
    async def login(self) -> Tuple[str, str]:
        """Getting access and refresh tokens. Opening a new session"""
        pass

    @abstractmethod
    async def logout(self) -> None:
        """Reset access tokens and refresh. Closing the session"""
        pass

    @abstractmethod
    async def logout_all(self) -> None:
        """Close all active user sessions"""
        pass

    @abstractmethod
    async def refresh_tokens(self) -> Tuple[str, str]:
        """Refresh access tokens and refresh"""
        pass

    @abstractmethod
    async def user_data(self) -> DBUser:
        """Get user data"""
        pass

    @abstractmethod
    async def user_role(self) -> str:
        """Get user role"""
        pass

    @abstractmethod
    async def update_user_data(self) -> DBUser:
        """Changing user data"""
        pass

    @abstractmethod
    async def update_user_password(self) -> None:
        """Changing user password"""
        pass

    @abstractmethod
    async def entry_history(self) -> List[DBEntry]:
        """Get user login history"""
        pass

    @abstractmethod
    async def deactivate_user(self) -> None:
        """Deactivate user"""
        pass


class AuthService(AuthServiceBase, HashManagerBase):
    def __init__(self,
                 token_db: TokenDBBase,
                 token_manager: TokenManagerBase,
                 user_db_session: AsyncSession,
                 ) -> None:
        self.token_db = token_db
        self.token_manager = token_manager
        self.user_db_session = user_db_session

    def hash_pwd(self, pwd: str) -> str:
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(pwd.encode('utf-8'), salt)
        return pwd_hash.decode('utf-8')

    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        return bcrypt.checkpw(pwd_in.encode('utf-8'), pwd_hash.encode('utf-8'))

    async def register(self, user: user_models.UserCreate, provider: str = None) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        # проверка на существование пользователя
        email_is_exist = await user_crud.get_by_email(user.email)
        login_is_exist = await user_crud.get_by_login(user.login)
        log.debug(f'User already exist: email={user.email}'
                  f' (exists = {email_is_exist});'
                  f' login={user.login} (exists = {login_is_exist})')
        if email_is_exist or login_is_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User already exist',
            )
        # добавление пользователя с хешированием пароля
        log.debug(f'Create new user: {user.login}')
        new_user = await user_crud.create(**user.dict(exclude={'password', }),
                                          password=self.hash_pwd(user.password.get_secret_value()),
                                          )
        if provider:
            user_social_crud = user_socials_dal.UserSocialDAL(self.user_db_session)
            new_user_social = await user_social_crud.create(new_user.uuid, user.login, provider=provider)
            log.debug(f'Create new user social: {new_user_social.user_id}, {provider=}')
        return new_user

    async def _generate_tokens(self,
                               user: DBUser,
                               entry: DBEntry,
                               ) -> Tuple[str, str]:
        role_crud = role_dal.RoleDAL(self.user_db_session)
        roles = await role_crud.get_by_user_id(user.uuid)
        token_payload = {
            'sub': str(user.uuid),
            'login': user.login,
            'role': [str(role.uuid) for role in roles],
        }
        access_token = await self.token_manager.generate_access_token(token_payload)
        token_payload.update({'session_id': str(entry.uuid)})
        refresh_token = await self.token_manager.generate_refresh_token(token_payload)
        return access_token, refresh_token

    async def login(self, login: str, pwd: SecretStr, user_agent: str) -> Tuple[str, str]:
        log_message = f'Login: {login}, pwd:{pwd}, user_agent:{user_agent}'
        log.debug(log_message)
        user_crud = user_dal.UserDAL(self.user_db_session)
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        # проверка наличия пользователя и совпадения пароля
        user = await user_crud.get_by_login(login)
        log_message = f'{user.login=}, {user.password=}, {user.uuid=}, {user.is_active=}'
        log.debug(log_message)
        if not user or not self.verify_pwd(pwd.get_secret_value(), user.password):
            log_message = f'Login {user.login}: ' \
                          f'user is exist = {bool(user)}, ' \
                          f'{pwd.get_secret_value()=}, {user.password=},' \
                          f' {self.verify_pwd(pwd.get_secret_value(), user.password)=}'
            log.debug(log_message)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Incorrect login or password',
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Account is not active',
            )

        exist_session = await entry_crud.get_by_user_agent(user_agent, only_active=True)

        if exist_session:
            log_msg = f'Login {user.login}: close session (refresh = {exist_session.refresh_token})'
            log.debug(log_msg)
            await self._close_session(exist_session.refresh_token)

        access_token, refresh_token = await self._open_session(user, user_agent)
        log_msg = f'{access_token=}, {refresh_token=}'
        log.debug(log_msg)
        return access_token, refresh_token

    async def _open_session(self, user: DBUser, user_agent: str) -> Tuple[str, str]:
        log_msg = f'Open session (user = {user})'
        log.debug(log_msg)
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        # записать сессию в БД
        session = await entry_crud.create(user.uuid, user_agent, None)
        log.info('Generate new tokens')
        access_token, refresh_token = await self._generate_tokens(user, session)
        # записать токен в БД
        await entry_crud.update(session.uuid, refresh_token=refresh_token)
        return access_token, refresh_token

    async def _close_session(self, refresh_token: str) -> None:
        if refresh_token is None:
            return
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        refresh_token_data = await self.token_manager.get_data_from_refresh_token(refresh_token)
        await entry_crud.delete(refresh_token_data.session_id)
        await self.token_db.put(refresh_token, refresh_token_data.sub, refresh_token_data.left_time)

    async def logout(self, access_token: str, refresh_token: str, user_agent: str = None):
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        access_token_data = await self.token_manager.get_data_from_access_token(access_token)
        user_id = access_token_data.sub
        # добавить в redis истекшие токены
        await self.token_db.put(access_token, user_id, access_token_data.left_time)

        if refresh_token is None:
            session = await entry_crud.get_by_user_agent(user_agent, only_active=True)
            await self._close_session(session.refresh_token)
        else:
            await self._close_session(refresh_token)

    async def logout_all(self, access_token: str) -> None:
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        access_token_data = await self.token_manager.get_data_from_access_token(access_token)
        user_id = access_token_data.sub
        await self.token_db.put(access_token, user_id, access_token_data.left_time)
        active_sessions = await entry_crud.get_by_user_id(user_id, only_active=True)
        for session in active_sessions:
            if session.refresh_token:
                await self._close_session(session.refresh_token)

    async def user_role(self, access_token: str) -> str:
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        return token_data.role

    async def entry_history(self, access_token: str, unique: bool, page_size: int, page_number: int) -> List[DBEntry]:
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        entry_history = await entry_crud.get_by_user_id(token_data.sub, unique=unique, page_size=page_size,
                                                        page_number=page_number)
        return entry_history

    async def user_data(self, access_token: str) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        user = await user_crud.get(token_data.sub)
        return user

    async def update_user_data(self, access_token: str, changed_data: user_models.ChangeUserData) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        updated_user_id = await user_crud.update(token_data.sub, **changed_data.dict(exclude_none=True))
        updated_user = await user_crud.get(updated_user_id)
        return updated_user

    async def update_user_password(self, access_token: str, refresh_token: str,
                                   changed_data: user_models.ChangeUserPwd) -> None:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        # проверка старого пароля
        user = await user_crud.get(token_data.sub)
        if not self.verify_pwd(changed_data.old_password.get_secret_value(), user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Incorrect old password',
            )
        # добавление нового пароля
        await user_crud.update(
            token_data.sub,
            password=self.hash_pwd(changed_data.new_password.get_secret_value())
        )
        log.info('Logout after changing password')
        await self.logout(access_token, refresh_token)

    async def refresh_tokens(self, refresh_token: str, user_agent: str) -> Tuple[str, str]:
        user_crud = user_dal.UserDAL(self.user_db_session)
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_refresh_token(refresh_token)
        log.info('Close old session after refresh tokens')
        await self._close_session(refresh_token)
        # получить пользователя по айди
        user = await user_crud.get(token_data.sub)
        # записать сессию в БД
        session = await entry_crud.create(user.uuid, user_agent, None)
        log.info('Generate new tokens')
        access_token, refresh_token = await self._generate_tokens(user, session)
        # записать токен в БД
        await entry_crud.update(session.uuid, refresh_token=refresh_token)
        return access_token, refresh_token

    async def deactivate_user(self, access_token: str):
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        await self.logout_all(access_token)
        await user_crud.delete(token_data.sub)


@lru_cache()
def get_auth_service(token_db: TokenDBBase = Depends(get_token_db),
                     token_manager: TokenManagerBase = Depends(get_token_manager),
                     user_db_session=Depends(get_db),
                     ) -> AuthService:
    log_msg = f'{token_db=}, {token_manager=}, {user_db_session=}'
    log.debug(log_msg)
    return AuthService(token_db, token_manager, user_db_session)
