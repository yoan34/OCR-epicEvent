FROM python:3.8.3-slim-buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app 