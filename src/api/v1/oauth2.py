import logging

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request, Response
from pydantic import SecretStr
from starlette.responses import HTMLResponse, RedirectResponse

from api.v1.models import UserResponse
from core.config import token_settings
from core.logger import LOGGING
from models.user import UserCreate
from utils.oauth_client import oauth
from services.auth import AuthServiceBase, get_auth_service

router = APIRouter(prefix='/oauth2')
logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

PASSWORD_SECRET_KEY = "123qwe"


@router.get('/login_oauth2')
async def login_oauth2(request: Request):
    redirect_uri = request.url_for('oauth2')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/register_oauth2')
async def register_oauth2(request: Request):
    redirect_uri = request.url_for('oauth2_registration')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/oauth2')
async def oauth2(request: Request, response: Response, auth_service: AuthServiceBase = Depends(get_auth_service)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')

    user = token.get('userinfo')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='No user from oauth2',
        )

    # generate some necessary values
    login = user['sub']
    password = SecretStr(login + PASSWORD_SECRET_KEY)

    access_token, refresh_token = await auth_service.login(login=login, pwd=password, user_agent="oauth2")
    log_msg = f'{access_token=}, {refresh_token=}'
    log.debug(log_msg)
    log.info('Set refresh token cookie')
    response.set_cookie(key=token_settings.refresh_token_cookie_name,
                        value=refresh_token,
                        httponly=True,
                        expires=token_settings.refresh_expire * 60,  # sec
                        )
    return access_token


@router.get('/oauth2_registration')
async def oauth2_registration(request: Request, auth_service: AuthServiceBase = Depends(get_auth_service)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')

    user = token.get('userinfo')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='No user from oauth2',
        )

    # generate some necessary values
    login = user['sub']
    name = user.get("given_name") or "name"
    surname = user.get("family_name") or "surname"
    email = user.get("email") or f"{login}@gmail.com"
    password = SecretStr(login + PASSWORD_SECRET_KEY)

    new_user = UserCreate(
        login=login,
        name=name,
        surname=surname,
        email=email,
        password=password
    )

    register_user = await auth_service.register(new_user, provider="google")
    return UserResponse.from_orm(register_user)


@router.get('/logout_oauth2')
async def logout_oauth2(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/auth_api/homepage')
