from os import environ
import multiprocessing

# REDIS配置
DEBUG = True
REDIS_HOST = environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = environ.get('REDIS_PORT') or 6379

# gunicorn配置
GUNICORN_WORKERS = environ.get(
    'GUNICORN_WORKERS') or multiprocessing.cpu_count() * 2 + 1
GUNICORN_TIMEOUT = environ.get('GUNICORN_TIMEOUT') or 20
GUNICORN_PORT = environ.get('GUNICORN_PORT') or 9004

WORKER_CLASS = environ.get('WORKER_CLASS') or 'sync'
GUNICORN_THREADS = environ.get('GUNICORN_THREADS') or (GUNICORN_WORKERS * 2)
MAX_REQUESTS = environ.get('MAX_REQUESTS') or 0
MAX_REQUESTS_JITTER = environ.get('MAX_REQUESTS_JITTER') or round(
    MAX_REQUESTS / 5)

LOG_LEVEL = environ.get('LOG_LEVEL') or 'DEBUG'

