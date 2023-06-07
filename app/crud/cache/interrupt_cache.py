import logging

from redis.exceptions import AuthenticationError, AuthorizationError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.exception.base_redis_om_error import BaseRedisOmError
from app.redis.file_status_model import FileStatusModel


class InterruptCache:
    @staticmethod
    async def save_interrupt_cache(
        unique_id: str,
        file_name: str,
        content: str,
        chunk_range: list[tuple[int, int]],
    ) -> None:
        try:
            file_status_obj = FileStatusModel(
                unique_id=unique_id,
                file_name=file_name,
                status="uploading",
                content=content,
                chunk_range=chunk_range,
            )
            await file_status_obj.save()
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
    async def update_interrupt_cache(unique_id: str, status: str) -> None:
        try:
            file_status_obj = await FileStatusModel.get(unique_id)
            file_status_obj.status = status
            await file_status_obj.save()
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
    async def get_interrupt_cache(unique_id: str) -> FileStatusModel:
        try:
            return await FileStatusModel.get(unique_id)
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
    async def delete_interrupt_cache(unique_id: str) -> None:
        try:
            await FileStatusModel.delete(unique_id)
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
    async def update_interrupt_chunk_range(unique_id: str, chunk_range: list[tuple[int, int]]) -> None:
        try:
            file_status_obj = await FileStatusModel.get(unique_id)
            file_status_obj.chunk_range = chunk_range
            await file_status_obj.save()
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
    async def get_all_pending_file_upload() -> list[FileStatusModel]:
        try:
            file_status_objects: list[FileStatusModel] = await FileStatusModel.find(
                FileStatusModel.status == "killed"
            ).all()
            return file_status_objects
        except (
            RedisTimeoutError,
            AuthenticationError,
            AuthorizationError,
            RedisConnectionError,
            BaseRedisOmError,
        ) as base_redis_error:
            logging.error(base_redis_error)
            raise base_redis_error
