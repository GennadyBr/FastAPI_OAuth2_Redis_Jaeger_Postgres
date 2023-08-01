import os
from core.logger import LOGGING

bind = '0.0.0.0:8081'
reload = True
worker_class = 'uvicorn.workers.UvicornWorker'
loglevel = os.getenv('LOG_LEVEL', 'DEBUG')
logconfig_dict = LOGGING