from AutoTestDjango.settings.base import *
from AutoTestDjango.settings.ENV import *

# python manage.py 启动的情况下会报错，本地环境增加
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# 存储文件相关的配置
MEDIA_ROOT = '/tmp/'
MEDIA_URL = '/media/'

DEBUG = True
BASE_REDIS = f'redis://{REDIS_HOST}:{REDIS_PORT}/'

REDIS_URL = BASE_REDIS + REDIS_DB


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_backend',
        'USER': 'test',
        'PASSWORD': 'Bl666666',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
