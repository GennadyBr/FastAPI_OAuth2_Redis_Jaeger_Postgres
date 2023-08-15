from pydantic import BaseSettings


class TestSettings(BaseSettings):
    redis_host: str = 'redis_token'
    redis_port: int = 6379

    servie_host: str = 'auth_test'
    service_port: int = 8081

    @property
    def service_url(cls):
        return f'http://{cls.servie_host}:{cls.service_port}'


class LoggerSettings(BaseSettings):
    format: str = "%(asctime)19s | %(levelname)s | %(message)s"
    datefmt: str = "%d.%m.%Y %H:%M:%S"
    level: str = "INFO"


test_settings = TestSettings()
logger_settings = LoggerSettings()
