import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from api.v1 import auth
from core.config import app_settings
from core.logger import LOGGING

app = FastAPI(
    title=app_settings.project_name,
    description='',
    summary='',
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


app.include_router(auth.router, prefix='/api/v1', tags=['auth'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        reload=True,
        log_config=LOGGING,
    )
