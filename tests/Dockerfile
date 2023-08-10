FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./tests ./tests

COPY ./core ./core
