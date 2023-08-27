import json
import logging

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

from api.v1.roles import router as role_router
from api.v1.auth import router as auth_router
from api.v1.oauth2 import router as oauth2_router
from core.logger import LOGGING
from core.config import app_settings
from utils.limits import check_limit

app = FastAPI(
    title=app_settings.project_name,
    description='Auth service for online cinema project',
    summary='API for getting information about users',
    version='0.0.1',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.add_middleware(SessionMiddleware, secret_key="secret-string")


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/api/v1/oauth2/logout_oauth2">logout oauth2</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/api/v1/oauth2/login_oauth2">login oauth2</a>')


@app.middleware("http")
async def before_request(request: Request, call_next):
    user_id = request.headers.get("X-Forwarded-For")
    result = await check_limit(user_id=user_id)
    if result:
        return ORJSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={'detail': 'Too many requests'}
        )
    return await call_next(request)


app.include_router(auth_router, prefix='/api/v1', tags=['auth'])
app.include_router(role_router, prefix='/api/v1', tags=['role'])
app.include_router(oauth2_router, prefix='/api/v1', tags=['oauth2'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        log_config=LOGGING,
        log_level=logging.getLevelName(app_settings.log_lvl),
    )
