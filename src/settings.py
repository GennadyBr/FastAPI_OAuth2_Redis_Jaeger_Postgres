from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
) #connect string to database
# postgresql+asyncpg - это драйвер подключения что бы алхимия синхронного подключалась
# postgres:postgres - это логин и пароль
