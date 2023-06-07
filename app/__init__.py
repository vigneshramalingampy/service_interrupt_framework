import logging

from aredis_om import Migrator
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.crud.database import initialize_database
from app.views.interrupt_view import interrupt_view


def create_app():
    fast_app = FastAPI(
        debug=settings.debug,
    )
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return fast_app


app: FastAPI = create_app()


@app.get("/", tags=["Health"])
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to service interrupt framework!",
            "status": "ok",
        },
        status_code=status.HTTP_200_OK,
    )


@app.get("/health", tags=["Health"])
async def health():
    return JSONResponse(
        content={
            "message": "Service is healthy!",
            "status": "ok",
        },
        status_code=status.HTTP_200_OK,
    )


def custom_openapi_schema():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Service Interrupt Framework",
        description="A framework for building service interrupt applications",
        version="1.0.0",
        routes=app.routes,
    )
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    for key, value in schemas.items():
        if "upload_file" in str(key):
            schemas[key]["title"] = "UploadFileSchema"
    openapi_schema.get("components", {}).get("schemas", {}).update(schemas)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi_schema

app.include_router(interrupt_view)


@app.on_event("startup")
async def startup_event():
    logging.info("Service is starting up!")
    await initialize_database()
    await Migrator().run()
