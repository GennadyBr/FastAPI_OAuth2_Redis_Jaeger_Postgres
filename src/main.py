import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from api.v1.roles import router as role_router
from api.v1.auth import router as auth_router
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


# @app.on_event('startup')
# async def startup():
#     redis = await get_cache()
#     es = await create_es()


# @app.on_event('shutdown')
# async def shutdown():
#     await redis.close()
#     await es.close()


app.include_router(auth_router, prefix='/api/v1', tags=['auth'])
app.include_router(role_router, prefix='/api/v1', tags=['role'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        log_config=LOGGING,
        log_level=logging.getLevelName(app_settings.log_lvl),
    )
