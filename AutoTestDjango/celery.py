import os

from celery import Celery

profile = os.environ.get('ENV', 'LOCAL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'AutoTestDjango.settings.{profile}')

app = Celery("django_celery")
app.conf.broker_pool_limit = None
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
