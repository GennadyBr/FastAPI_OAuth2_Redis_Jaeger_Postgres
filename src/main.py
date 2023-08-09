import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from api.v1.roles import router as role_router
from core.logger import LOGGING
from core.config import app_settings

app = FastAPI(
    title=app_settings.project_name,
    description='Auth service for online cinema project',
    summary='API for getting information about users',
    version='0.0.1',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

main_api_router = APIRouter()

main_api_router.include_router(role_router, prefix="/role", tags=["role"])
app.include_router(main_api_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        log_config=LOGGING,
        log_level=logging.getLevelName(app_settings.log_lvl),
    )
