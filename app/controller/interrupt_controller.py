import asyncio
import logging
import uuid

from aredis_om import NotFoundError
from fastapi import UploadFile
from redis import AuthenticationError
from redis.exceptions import AuthorizationError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.crud.cache.interrupt_cache import InterruptCache
from app.crud.database.interrupt_database import InterruptDatabase
from app.exception.base_alchemy_exception import BaseAlchemyException
from app.exception.base_redis_om_error import BaseRedisOmError
from app.models.response.default_response_model import DefaultResponseModel
from app.redis.file_status_model import FileStatusModel

# FILE_SIZE_LIMIT = 65000


FILE_SIZE_LIMIT = 5


class InterruptController:
    @staticmethod
    async def upload_file(file: UploadFile) -> DefaultResponseModel:
        try:
            unique_id: str = uuid.uuid4().__str__()
            content_bytes: bytes = await file.read()
            content: str = content_bytes.decode("utf-8")
            if len(content) < FILE_SIZE_LIMIT:
                await InterruptDatabase.upload_file(
                    unique_id=unique_id,
                    content=content,
                    file_name=file.filename,
                    file_size="small",
                )
                return DefaultResponseModel(
                    message="File uploaded successfully",
                    status="success",
                    status_code=200,
                )
            chunks_range = [(i, i + FILE_SIZE_LIMIT) for i in range(0, len(content), FILE_SIZE_LIMIT)]

            await InterruptCache.save_interrupt_cache(
                unique_id=unique_id, chunk_range=chunks_range, file_name=file.filename, content=content
            )
            asyncio.create_task(InterruptController.upload_file_task(file.filename, unique_id, content, chunks_range))
            return DefaultResponseModel(
                message="File upload in progress please check status with unique id",
                status="success",
                status_code=200,
                data={"unique_id": unique_id},
            )
        except BaseAlchemyException as base_alchemy_error:
            logging.error(base_alchemy_error)
            raise base_alchemy_error

    @staticmethod
    async def upload_file_task(
        filename: str,
        unique_id: str,
        content: str,
        chunks_range: list[tuple[int, int]],
    ) -> None:
        try:
            chunks_range_copy = chunks_range.copy()
            for index, chunk_range in enumerate(chunks_range):
                file_status_obj: FileStatusModel = await InterruptCache.get_interrupt_cache(unique_id)

                if file_status_obj.status.value in ["killed", "stopped"]:
                    break

                chunk = content[chunk_range[0] : chunk_range[1]]

                await InterruptDatabase.upload_file(
                    unique_id=unique_id,
                    content=chunk,
                    file_name=filename,
                    file_size="large",
                )

                chunks_range_copy.remove(chunk_range)
                await InterruptCache.update_interrupt_chunk_range(unique_id, chunks_range_copy)
                # await sleep(10)

            if len(chunks_range_copy) == 0:
                await InterruptDatabase.update_file_status(unique_id, "completed")
                await InterruptCache.delete_interrupt_cache(unique_id)

        except BaseAlchemyException as base_alchemy_error:
            logging.error(base_alchemy_error)
            raise base_alchemy_error

    @staticmethod
    async def kill_file_upload(unique_id: str) -> DefaultResponseModel:
        try:
            file_status_obj: FileStatusModel = await InterruptCache.get_interrupt_cache(unique_id)
            if file_status_obj is not None:
                await InterruptCache.update_interrupt_cache(unique_id, "killed")
                return DefaultResponseModel(
                    message="File upload killed successfully",
                    status="success",
                    status_code=200,
                )
        except NotFoundError as not_found_error:
            logging.error(not_found_error)
            raise not_found_error
        except (
            RedisTimeoutError,
            AuthenticationError,
            AuthorizationError,
            RedisConnectionError,
            BaseRedisOmError,
        ) as base_redis_error:
            logging.error(base_redis_error)
            raise base_redis_error

    @staticmethod
    async def get_all_pending_file_upload() -> DefaultResponseModel:
        try:
            file_status_objs: list[FileStatusModel] = await InterruptCache.get_all_pending_file_upload()
            upload_id: list[str] = []
            for file_status_obj in file_status_objs:
                upload_id.append(file_status_obj.unique_id)
            return DefaultResponseModel(
                message="Fetched all pending file uploads successfully",
                status="success",
                status_code=200,
                data={"upload_id": upload_id},
            )
        except (
            RedisTimeoutError,
            AuthenticationError,
            AuthorizationError,
            RedisConnectionError,
            BaseRedisOmError,
        ) as base_redis_error:
            logging.error(base_redis_error)
            raise base_redis_error

    @staticmethod
    async def resume_upload(upload_id: str):
        try:
            await InterruptCache.update_interrupt_cache(upload_id, "uploading")
            cached_date: FileStatusModel = await InterruptCache.get_interrupt_cache(upload_id)
            asyncio.create_task(
                InterruptController.upload_file_task(
                    cached_date.file_name,
                    upload_id,
                    cached_date.content,
                    cached_date.chunk_range,
                )
            )
            return DefaultResponseModel(
                message="File upload resumed successfully",
                status="success",
                status_code=200,
                data={"upload_id": upload_id},
            )
        except (
            RedisTimeoutError,
            AuthenticationError,
            AuthorizationError,
            RedisConnectionError,
            BaseRedisOmError,
        ) as base_redis_error:
            logging.error(base_redis_error)
            raise base_redis_error

    @staticmethod
    async def stop_upload(upload_id: str):
        try:
            await InterruptCache.update_interrupt_cache(upload_id, "stopped")
            await InterruptDatabase.delete_file_upload(upload_id)
            await InterruptCache.delete_interrupt_cache(upload_id)
            return DefaultResponseModel(
                message="File upload stopped successfully",
                status="success",
                status_code=200,
            )
        except (
            RedisTimeoutError,
            AuthenticationError,
            AuthorizationError,
            RedisConnectionError,
            BaseRedisOmError,
        ) as base_redis_error:
            logging.error(base_redis_error)
            raise base_redis_error
