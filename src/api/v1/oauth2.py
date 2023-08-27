from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter
from fastapi import Request
from starlette.responses import HTMLResponse, RedirectResponse

from utils.oauth_client import oauth

router = APIRouter(prefix='/oauth2')


@router.get('/login_oauth2')
async def login_oauth2(request: Request):
    redirect_uri = request.url_for('oauth2')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/oauth2')
async def oauth2(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@router.get('/logout_oauth2')
async def logout_oauth2(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
