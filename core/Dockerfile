FROM python:3.10-slim

WORKDIR /code

RUN apt-get update && apt-get -y install libpq-dev gcc curl

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./core ./core

COPY ./migrations ./migrations

COPY ./alembic.ini ./alembic.ini