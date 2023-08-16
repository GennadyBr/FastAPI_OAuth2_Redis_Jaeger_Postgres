import logging
import os
import sys
import requests

import backoff


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from settings import test_settings, logger_settings


logging.basicConfig(
    format=logger_settings.format,
    level=logging.getLevelName(logger_settings.level),
    datefmt=logger_settings.datefmt,
)


@backoff.on_exception(backoff.expo, requests.exceptions.ConnectionError, max_tries=100, raise_on_giveup=False)
def waiting_auth():
    logging.info('Waiting for auth')
    requests.get(test_settings.service_url)
    logging.info('Done auth!')


if __name__ == '__main__':
    waiting_auth()