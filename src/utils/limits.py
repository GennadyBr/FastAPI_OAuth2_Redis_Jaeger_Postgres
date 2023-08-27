import datetime
from redis.asyncio import Redis

from core.config import redis_settings, jwt_settings

redis_conn = Redis(host=redis_settings.host, port=redis_settings.port, password=redis_settings.password.get_secret_value(), db=1)

async def check_limit(user_id: str) -> bool:
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f'{user_id}:{now.minute}'
    await pipe.incr(key, 1)
    await pipe.expire(key, 59)
    result = await pipe.execute()
    request_number = result[0]
    return request_number > jwt_settings.REQUEST_LIMIT_PER_MINUTE
