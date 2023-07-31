FROM python:3.10-slim

WORKDIR /code

RUN apt-get update && apt-get -y install curl

COPY ./core_requirements.txt ./core_requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./core_requirements.txt

COPY ./core ./core

COPY ./migrations ./migrations

COPY ./alembic.ini ./alembic.ini