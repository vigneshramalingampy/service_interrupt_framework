import logging
from typing import Literal

from sqlalchemy import String, cast, delete, update
from sqlalchemy.ext.asyncio import async_scoped_session

from app.crud.database import session
from app.exception.base_alchemy_exception import BaseAlchemyException
from app.sql.file_content_model import FileContentModel, FileUploadStatus

INTERMEDIATE_STATUS = {"large": FileUploadStatus.UPLOADING, "small": FileUploadStatus.COMPLETED}


class InterruptDatabase:
    @staticmethod
    @session
    async def upload_file(
        async_session,
        unique_id: str,
        content: str,
        file_name: str,
        file_size: Literal["large", "small"],
    ) -> None:
        try:
            file_object = FileContentModel(
                file_id=unique_id,
                file_name=file_name,
                content=content,
                status=INTERMEDIATE_STATUS[file_size],
            )
            async_session.add(file_object)
            await async_session.commit()
        except BaseAlchemyException as base_alchemy_error:
            logging.error(base_alchemy_error)
            raise base_alchemy_error

    @staticmethod
    @session
    async def update_file_status(
        async_session: async_scoped_session,
        unique_id: str,
        status: str,
    ) -> None:
        try:
            file_status: FileUploadStatus | None = None
            if status == "killed":
                file_status = FileUploadStatus.KILLED
            elif status == "completed":
                file_status = FileUploadStatus.COMPLETED
            elif status == "uploading":
                file_status = FileUploadStatus.UPLOADING
            statement = (
                update(FileContentModel)
                .where(cast(FileContentModel.file_id, String) == unique_id)
                .values(
                    {
                        FileContentModel.status: file_status,
                    }
                )
            )
            await async_session.execute(statement)
            await async_session.commit()
        except BaseAlchemyException as base_alchemy_error:
            logging.error(base_alchemy_error)
            raise base_alchemy_error

    @staticmethod
    @session
    async def delete_file_upload(
        async_session: async_scoped_session,
        unique_id: str,
    ) -> None:
        try:
            statement = delete(FileContentModel).where(cast(FileContentModel.file_id, String) == unique_id)
            await async_session.execute(statement)
            await async_session.commit()
        except BaseAlchemyException as base_alchemy_error:
            logging.error(base_alchemy_error)
            raise base_alchemy_error
