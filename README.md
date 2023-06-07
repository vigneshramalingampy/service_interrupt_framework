# Service Interrupt Framework

A file upload service interrupt framework build with FastAPI.

## Steps to run the project without docker

## Installation

1. Install Python 3.8 >= `brew install python3`

2. Install poetry `pip3 install poetry`

3. Inside your project directory, run `poetry install`

4. Install postgresql `brew install postgresql`

5. Set environment value `export DATABASE_URL=postgresql://postgres:postgres@database:5432/service_interrupt` or set it
   in your `.env` file

6. Also set other needed values in `.env` file

```bash
export  DATABASE_URL=postgresql+asyncpg://postgres:postgres@database:5432/service_interrupt
export  DEBUG=false
export  ENVIRONMENT=development
export  REDIS_OM_URL=redis://default:QJXbMO4mM1OBXbkK9tBhdN1pv0uoBTqX@redis-18888.c212.ap-south-1-1.ec2.cloud.redislabs.com:18888
export  DB_USERNAME=postgres
export  DB_PASSWORD=postgres
export  DB_NAME=service_interrupt

```

## Steps to run the project

1. Spawn a shell with `poetry shell`
2. Run `uvicorn app:app --reload`

## Steps to run the app inside docker

1. `docker-compose up`