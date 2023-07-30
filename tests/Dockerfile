FROM python:3.10-slim

WORKDIR /code

RUN pip install --no-cache-dir --upgrade httpx==0.24.1 pytest==7.4.0 python-dotenv==1.0.0

COPY ./tests ./tests