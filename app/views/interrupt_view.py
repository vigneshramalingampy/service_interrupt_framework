from aredis_om import NotFoundError
from fastapi import APIRouter, UploadFile
from redis import AuthenticationError
from redis.exceptions import AuthorizationError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.controller.interrupt_controller import InterruptController
from app.exception.base_alchemy_exception import BaseAlchemyException
from app.exception.base_redis_om_error import BaseRedisOmError
from app.models.response.default_response_model import DefaultResponseModel

interrupt_view: APIRouter = APIRouter(
    prefix="/interrupt",
    tags=["Interrupt"],
)


@interrupt_view.post(
    "/upload_file",
    response_model=DefaultResponseModel,
    response_model_exclude_none=True,
)
async def upload_file(file: UploadFile):
    if file.content_type != "text/plain" or file.filename.split(".")[-1] != "txt":
        return DefaultResponseModel(
            message="Only text file is allowed",
            status="error",
            status_code=400,
            data=None,
        )
    try:
        response: DefaultResponseModel = await InterruptController.upload_file(file)
        return response
    except BaseAlchemyException as base_alchemy_error:
        return DefaultResponseModel(
            message=base_alchemy_error.args[0],
            status="error",
            status_code=500,
            data=None,
        )


@interrupt_view.post(
    "/kill/{upload_id}",
    response_model=DefaultResponseModel,
    response_model_exclude_none=True,
)
async def kill_file_upload(upload_id: str):
    try:
        response: DefaultResponseModel = await InterruptController.kill_file_upload(upload_id)
        return response
    except NotFoundError as not_found_error:
        return DefaultResponseModel(
            message=f"The file upload is either completed or not found{not_found_error}",
            status="error",
            status_code=404,
            data=None,
        )
    except (
        RedisTimeoutError,
        AuthenticationError,
        AuthorizationError,
        RedisConnectionError,
        BaseRedisOmError,
    ) as base_redis_error:
        return DefaultResponseModel(
            message=base_redis_error.args[0],
            status="error",
            status_code=500,
            data=None,
        )


@interrupt_view.get(
    "/pending_uploads",
    response_model=DefaultResponseModel,
    response_model_exclude_none=True,
)
async def get_pending_file_uploads():
    try:
        response: DefaultResponseModel = await InterruptController.get_all_pending_file_upload()
        return response
    except (
        RedisTimeoutError,
        AuthenticationError,
        AuthorizationError,
        RedisConnectionError,
        BaseRedisOmError,
    ) as base_redis_error:
        return DefaultResponseModel(
            message=base_redis_error.args[0],
            status="error",
            status_code=500,
            data=None,
        )


@interrupt_view.get(
    "/resume/{upload_id}",
    response_model=DefaultResponseModel,
    response_model_exclude_none=True,
)
async def resume_upload(upload_id: str):
    try:
        response: DefaultResponseModel = await InterruptController.resume_upload(upload_id=upload_id)
        return response
    except (
        RedisTimeoutError,
        AuthenticationError,
        AuthorizationError,
        RedisConnectionError,
        BaseRedisOmError,
    ) as base_redis_error:
        return DefaultResponseModel(
            message=base_redis_error.args[0],
            status="error",
            status_code=500,
            data=None,
        )


@interrupt_view.delete(
    "/stop",
    response_model_exclude_none=True,
)
async def stop_upload(upload_id: str):
    try:
        response: DefaultResponseModel = await InterruptController.stop_upload(upload_id=upload_id)
        return response
    except (
        RedisTimeoutError,
        AuthenticationError,
        AuthorizationError,
        RedisConnectionError,
        BaseRedisOmError,
    ) as base_redis_error:
        return DefaultResponseModel(
            message=base_redis_error.args[0],
            status="error",
            status_code=500,
            data=None,
        )
