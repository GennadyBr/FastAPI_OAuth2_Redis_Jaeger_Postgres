import logging
import os
import sys
import time

import backoff
from redis.client import Redis
from redis.exceptions import ConnectionError as RedisConEr

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from settings import test_settings, logger_settings

logging.basicConfig(
    format=logger_settings.format,
    level=logging.getLevelName(logger_settings.level),
    datefmt=logger_settings.datefmt,
)


@backoff.on_exception(backoff.expo, RedisConEr, max_tries=100, raise_on_giveup=False)
def waiting_redis():
    redis_client = Redis(host=test_settings.redis_host,
                         port=test_settings.redis_port,
                         password=test_settings.redis_password.get_secret_value(),
                         )
    while True:
        logging.info('Waiting for redis')
        if redis_client.ping():
            break
        time.sleep(1)

    logging.info('Done Redis!')


if __name__ == '__main__':
    waiting_redis()
