FROM python:3.10-slim

WORKDIR /code

COPY ./celery_app/celery_requirements.txt ./celery_app/celery_requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./celery_app/celery_requirements.txt

COPY ./celery_app/tasks.py ./celery_app/tasks.py
