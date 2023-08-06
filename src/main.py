import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from api.user_handlers import user_router
from api.role_handlers import role_router
from api.entry_handlers import entry_router
from core.logger import LOGGING
from core.config import auth_settings

app = FastAPI(
    title=auth_settings.project_name,
    description='Auth service for online cinema project',
    summary='API for getting information about users',
    version='0.0.1',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

# create the instance for the routes
main_api_router = APIRouter()  # инициализируем роутер для любых адресов, роутер который будет собирать остальные роутеры

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user",
                               tags=["user"])  # включаем user_router в main_api_router c путем "/user"
main_api_router.include_router(role_router, prefix="/role",
                               tags=["role"])  # включаем role_router в main_api_router c путем "/role"
main_api_router.include_router(entry_router, prefix="/entry",
                               tags=["entry"])  # включаем entry_router в main_api_router c путем "/entry"
app.include_router(main_api_router)  # даем доступ main_api_router в приложение app FastAPI

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        log_config=LOGGING,
        log_level=logging.getLevelName(auth_settings.log_lvl),
    )
