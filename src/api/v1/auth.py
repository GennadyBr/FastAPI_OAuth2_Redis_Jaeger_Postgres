from typing import List, Annotated

from fastapi import APIRouter, Depends, Header, Response, Cookie, Query

from core.config import token_settings
from .models import UserCreateRequest, ChangeUserPwdRequest, ChangeUserDataRequest, UserResponse, LoginRequest, \
    EntryResponse
from models.user import UserCreate, ChangeUserData, ChangeUserPwd
from utils.token_manager import verify_access_token, verify_refresh_token
from services.auth import AuthServiceBase, get_auth_service

router = APIRouter(prefix='/auth')


@router.post('/register',
             response_model=UserResponse,
             summary="Post request for register new user",
             description="Creates a new user and returns a new user object",
             response_description="New user auth data",
             )
async def register(user: UserCreateRequest,
                   auth_service: AuthServiceBase = Depends(get_auth_service),
                   ) -> UserResponse:
    register_user = await auth_service.register(UserCreate(**user.dict()))
    return UserResponse.from_orm(register_user)


@router.post('/login',
             response_model=str,
             summary="Post request for login exist user",
             description="Creates access and refresh tokens",
             response_description="Access token",
             )
async def login(user: LoginRequest,
                response: Response,
                auth_service: AuthServiceBase = Depends(get_auth_service),
                user_agent: str = Header(include_in_schema=False),
                ) -> str:
    access_token, refresh_token = await auth_service.login(login=user.login,
                                                           pwd=user.password,
                                                           user_agent=user_agent,
                                                           )
    response.set_cookie(key=token_settings.refresh_token_cookie_name,
                        value=refresh_token,
                        httponly=True,
                        expires=token_settings.refresh_expire * 60,  # sec
                        )
    return access_token


@router.post('/refresh',
             response_model=str,
             summary="Post request for refresh access token",
             description="Creates new access and refresh tokens",
             response_description="New access token",
             )
async def refresh(response: Response,
                  auth_service: AuthServiceBase = Depends(get_auth_service),
                  refresh_token: str = Depends(verify_refresh_token),
                  user_agent: str = Header(include_in_schema=False),
                  ) -> str:
    new_access_token, new_refresh_token = await auth_service.refresh_tokens(refresh_token=refresh_token,
                                                                            user_agent=user_agent)
    response.set_cookie(key=token_settings.refresh_token_cookie_name,
                        value=new_refresh_token,
                        httponly=True,
                        expires=token_settings.refresh_expire * 60,  # sec
                        )
    return new_access_token


@router.get('/me',
            response_model=UserResponse,
            summary="Get request for user information",
            description="Gives user information by access token",
            response_description="User data",
            )
async def user_data(token: str = Depends(verify_access_token),
                    auth_service: AuthServiceBase = Depends(get_auth_service),
                    ) -> UserResponse:
    user_data = await auth_service.user_data(token)
    return UserResponse.from_orm(user_data)


@router.get('/entries',
            response_model=List[EntryResponse],
            summary="Get request for user entries history",
            description="Gives user entries by access token",
            response_description="User entries",
            )
async def user_entries(unique: bool = True,
                       token: str = Depends(verify_access_token),
                       auth_service: AuthServiceBase = Depends(get_auth_service),
                       page_size: Annotated[int, Query(description="Pagination page size", ge=1)] = 10,
                       page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
                       ) -> List[EntryResponse]:
    user_entries = await auth_service.entry_history(token, unique, page_size, page_number)
    return [EntryResponse.from_orm(entry) for entry in user_entries]


@router.get('/role',
            response_model=List[str],
            summary="Get request for user roles",
            description="Gives user roles by access token",
            response_description="User roles",
            )
async def user_role(token: str = Depends(verify_access_token),
                    auth_service: AuthServiceBase = Depends(get_auth_service),
                    ) -> List[str]:
    role = await auth_service.user_role(token)
    return role


@router.get('/logout',
            summary="Get request for logout from active session",
            description="Closes the user session and deletes access and refresh tokens",
            response_description="Null",
            )
async def logout(response: Response,
                 access_token: str = Depends(verify_access_token),
                 refresh_token: Annotated[str, Cookie(include_in_schema=False)] = None,
                 user_agent: str = Header(include_in_schema=False),
                 auth_service: AuthServiceBase = Depends(get_auth_service),
                 ) -> None:
    await auth_service.logout(access_token, refresh_token, user_agent)
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@router.get('/logout_all',
            summary="Get request for logout from all active sessions",
            description="Closes the user sessions and deletes access and refresh tokens",
            response_description="Null",
            )
async def logout_all(response: Response,
                     token: str = Depends(verify_access_token),
                     auth_service: AuthServiceBase = Depends(get_auth_service),
                     ) -> None:
    await auth_service.logout_all(token)
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@router.post('/change_pwd',
             summary="Post request for change user password",
             description="Change user password and logout",
             response_description="Null",
             )
async def change_pwd(changed_pwd_data: ChangeUserPwdRequest,
                     response: Response,
                     access_token: str = Depends(verify_access_token),
                     refresh_token: Annotated[str, Cookie(include_in_schema=False)] = None,
                     auth_service: AuthServiceBase = Depends(get_auth_service),
                     ) -> None:
    await auth_service.update_user_password(access_token,
                                            refresh_token,
                                            ChangeUserPwd(**changed_pwd_data.dict(exclude={'new_password_repeat'})),
                                            )
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@router.post('/change_user_data',
             response_model=UserResponse,
             summary="Post request for change user information",
             description="Change user information",
             response_description="User information",
             )
async def change_user_data(changed_user_data: ChangeUserDataRequest,
                           token: str = Depends(verify_access_token),
                           auth_service: AuthServiceBase = Depends(get_auth_service),
                           ) -> UserResponse:
    updated_user = await auth_service.update_user_data(token, ChangeUserData(**changed_user_data.dict()))
    return UserResponse.from_orm(updated_user)


@router.post('/deactivate_user',
             summary="Post request for deactivate user",
             description="Inactivate user's account",
             response_description="Null",
             )
async def deactivate_user(response: Response,
                          token: str = Depends(verify_access_token),
                          auth_service: AuthServiceBase = Depends(get_auth_service),
                          ) -> None:
    await auth_service.deactivate_user(token)
    response.delete_cookie(token_settings.refresh_token_cookie_name)
