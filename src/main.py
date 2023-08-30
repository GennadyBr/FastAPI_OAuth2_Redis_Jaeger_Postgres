import json
import logging
import logging.config

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from api.v1.roles import router as role_router
from api.v1.auth import router as auth_router
from api.v1.oauth2 import router as oauth2_router
from core.logger import LOGGING
from utils.limits import check_limit
from core.config import app_settings, jaeger_settings, enable_tracer

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

PREFIX = "/auth_api"


def configure_tracer() -> None:
    """
    Трейсер - константный сэмплер, для трейсинга всех запросов.
    По умолчанию Jaeger сэмплирует только порядка 5%.
    """
    resource = Resource(attributes={
        SERVICE_NAME: 'auth-service'
    })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaeger_settings.host,
                agent_port=jaeger_settings.port_udp,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

if enable_tracer:
    configure_tracer()  # Jaeger instrument for tracer, must be before app = FastAPI

app = FastAPI(
    title=app_settings.project_name,
    description='Auth service for online cinema project',
    summary='API for getting information about users',
    version='0.0.1',
    docs_url=f'{PREFIX}/openapi',
    openapi_url=f'{PREFIX}/openapi.json',
    default_response_class=ORJSONResponse,
)

FastAPIInstrumentor.instrument_app(app)  # Jaeger instrument for tracer, must be after app = FastAPI

app.add_middleware(SessionMiddleware, secret_key="secret-string")


@app.get(f'{PREFIX}/homepage')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            f'<a href="{PREFIX}/v1/oauth2/logout_oauth2">logout oauth2</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse(
        f'<a href="{PREFIX}/v1/oauth2/login_oauth2">login oauth2</a> '
        + f'<a href="{PREFIX}/v1/oauth2/register_oauth2">register oauth2</a>')


@app.middleware("http")
async def before_request_check_limit(request: Request, call_next):
    user_id = request.headers.get("X-Forwarded-For")
    result = await check_limit(user_id=user_id)
    if result:
        return ORJSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={'detail': 'Too many requests'}
        )
    return await call_next(request)


@app.middleware('http')
async def before_request_add_headers(request: Request, call_next):
    """
    Обработчик заголовка X-Request-Id.
    """
    response = await call_next(request)
    log.info('<<<request_id middleware>>>')
    request_id = request.headers.get('X-Request-Id', None)
    log_msg = f'{request_id=}'
    log.debug(log_msg)
    return response


app.include_router(auth_router, prefix=f'{PREFIX}/v1', tags=['auth'])
app.include_router(role_router, prefix=f'{PREFIX}/v1', tags=['role'])
app.include_router(oauth2_router, prefix=f'{PREFIX}/v1', tags=['oauth2'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        log_config=LOGGING,
        log_level=logging.getLevelName(app_settings.log_lvl),
    )
