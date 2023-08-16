import logging
import os
import sys
import time

import backoff
import psycopg2


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from core.config import user_db_settings
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logging.getLogger(__name__)

@backoff.on_exception(backoff.expo, psycopg2.OperationalError, max_tries=100, raise_on_giveup=False)
def waiting_pg():
    pg_conn = psycopg2.connect(
            dbname=user_db_settings.name,
            user=user_db_settings.user,
            password=user_db_settings.password.get_secret_value(),
            host=user_db_settings.service_name,
            port=user_db_settings.port,
        )
    while True:
        logging.info('Waiting for pg')
        
        try:
            cur = pg_conn.cursor()
            cur.execute('SELECT 1')
            break
        except psycopg2.OperationalError:
            pass
        
        time.sleep(1)

    logging.info('Done PG!')


if __name__ == '__main__':
    waiting_pg()