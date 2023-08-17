from pydantic import BaseSettings, AnyUrl, SecretStr


class UserDBSettings(BaseSettings):
    name: str
    user: str
    password: SecretStr
    port: int = 5432
    service_name: str = 'db_users'

    class Config:
        env_prefix = 'pg_db_'

    def _url(cls, asyncpg: bool = False) -> AnyUrl:
        return f'postgresql{"+asyncpg" * asyncpg}://{cls.user}:{cls.password.get_secret_value()}@{cls.service_name}' \
               f':{cls.port}/{cls.name}'

    @property
    def url(cls) -> AnyUrl:
        return cls._url()

    @property
    def async_url(cls) -> AnyUrl:
        return cls._url(asyncpg=True)


class TestSettings(BaseSettings):
    redis_host: str = 'redis_token_test'
    redis_port: int = 6379
    redis_password: SecretStr = ''

    servie_host: str = 'auth_test'
    service_port: int = 8081

    @property
    def service_url(cls):
        return f'http://{cls.servie_host}:{cls.service_port}'


class TokenSettings(BaseSettings):
    access_expire: int = 10  # min
    access_secret_key: SecretStr = ''
    refresh_expire: int = 60  # min
    refresh_secret_key: SecretStr = ''
    refresh_token_cookie_name: str = 'refresh_token'
    algorithm: str = 'HS256'

    class Config:
        env_prefix = 'token_'


class LoggerSettings(BaseSettings):
    format: str = "%(asctime)19s | %(levelname)s | %(message)s"
    datefmt: str = "%d.%m.%Y %H:%M:%S"
    level: str = "INFO"


test_settings = TestSettings()
user_db_settings = UserDBSettings()
token_settings = TokenSettings()
logger_settings = LoggerSettings()
