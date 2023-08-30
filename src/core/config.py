from logging import config as logging_config

from pydantic import BaseSettings, AnyUrl, SecretStr

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

enable_tracer = True


class APPSettings(BaseSettings):
    project_name: str = 'Auth API'
    log_lvl: str = 'DEBUG'


class UserDBSettings(BaseSettings):
    name: str
    user: str
    password: SecretStr
    port: int = 5432
    service_name: str = 'db_users'

    class Config:
        env_prefix = 'pg_db_'

    def _url(cls, asyncpg: bool = False) -> AnyUrl:
        return f'postgresql{"+asyncpg" * asyncpg}://{cls.user}' \
               f':{cls.password.get_secret_value()}@{cls.service_name}:{cls.port}/{cls.name}'

    @property
    def url(cls) -> AnyUrl:
        return cls._url()

    @property
    def async_url(cls) -> AnyUrl:
        return cls._url(asyncpg=True)


class TokenSettings(BaseSettings):
    access_expire: int = 10  # min
    access_secret_key: SecretStr = ''
    refresh_expire: int = 60  # min
    refresh_secret_key: SecretStr = ''
    refresh_token_cookie_name: str = 'refresh_token'
    algorithm: str = 'HS256'

    class Config:
        env_prefix = 'token_'


class RedisSettings(BaseSettings):
    host: str = 'redis_token'
    port: int = 6379
    password: SecretStr = ''

    class Config:
        env_prefix = 'redis_'


class JWTSetting(BaseSettings):
    REQUEST_LIMIT_PER_MINUTE: int = 20


class JaegerSettings(BaseSettings):
    host: str = 'jaeger'
    port_udp: int = 6831
    port_tcp: int = 16686

    class Config:
        env_prefix = 'jaeger_'


class Oauth2Settings(BaseSettings):
    PASSWORD_GEN_SECRET_KEY: str = "123qwe"


app_settings = APPSettings()
token_settings = TokenSettings()
redis_settings = RedisSettings()
user_db_settings = UserDBSettings()
jwt_settings = JWTSetting()
jaeger_settings = JaegerSettings()
oauth2_settings = Oauth2Settings()
