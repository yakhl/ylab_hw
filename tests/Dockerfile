FROM python:3.10-slim

WORKDIR /code

COPY ./tests_requirements.txt ./tests_requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./tests_requirements.txt

COPY ./tests ./tests