import enum

from sqlalchemy import Column, Enum, Text

from app.sql.base import BaseModel


class FileUploadStatus(enum.Enum):
    UPLOADING = "uploading"
    COMPLETED = "completed"
    KILLED = "killed"


class FileContentModel(BaseModel):
    __tablename__ = "file_content"

    file_name = Column(Text, nullable=False)
    file_id = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(FileUploadStatus), nullable=False, default=FileUploadStatus.UPLOADING)
