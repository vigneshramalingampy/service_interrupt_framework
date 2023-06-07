FROM python:3.11-alpine3.17

ENV DATABASE_URL='postgresql+asyncpg://postgres:postgres@database:5432/service_interrupt' \
    ENVIRONMENT='development' \
    DEBUG=false \
    REDIS_OM_URL='redis://default:QJXbMO4mM1OBXbkK9tBhdN1pv0uoBTqX@redis-18888.c212.ap-south-1-1.ec2.cloud.redislabs.com:18888' \
    DB_USERNAME='postgres' \
    DB_PASSWORD='postgres' \
    DB_NAME='service_interrupt'



WORKDIR /service_interrupt_framework

COPY ./requirements.txt /service_interrupt_framework/requirements.txt

RUN export REDIS_OM_URL='redis://default:QJXbMO4mM1OBXbkK9tBhdN1pv0uoBTqX@redis-18888.c212.ap-south-1-1.ec2.cloud.redislabs.com:18888'
RUN apk add gcc libc-dev libffi-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /service_interrupt_framework/requirements.txt


COPY . /service_interrupt_framework

EXPOSE 8000