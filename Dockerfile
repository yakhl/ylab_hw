FROM python:3.10-slim

RUN apt-get update && apt-get -y install libpq-dev gcc

WORKDIR /code

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./core ./core

COPY ./migrations ./migrations

COPY ./alembic.ini ./alembic.ini