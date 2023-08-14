import os

import httpx
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

FASTAPI_HOST = os.environ.get('FASTAPI_HOST', 'localhost')
FASTAPI_PORT = os.environ.get('FASTAPI_PORT', '8000')
RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = os.environ.get('RABBIT_PORT', '5672')

celery = Celery('tasks', broker=f'pyamqp://guest@{RABBIT_HOST}:{RABBIT_PORT}//', backend='rpc://')

celery.conf.beat_schedule = {
    'sync-table-every-15-seconds': {
        'task': 'celery_app.tasks.sync_table',
        'schedule': 15.0,
    },
}


@celery.task
def sync_table():
    with httpx.Client() as client:
        response = client.post(f'http://{FASTAPI_HOST}:{FASTAPI_PORT}/api/v1/admin/sync_table')
        return response.text
