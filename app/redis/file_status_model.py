import enum

from aredis_om import Field, JsonModel


class FileUploadStatus(str, enum.Enum):
    UPLOADING = "uploading"
    COMPLETED = "completed"
    KILLED = "killed"
    STOPPED = "stopped"


class FileStatusModel(JsonModel):
    unique_id: str = Field(primary_key=True, index=True)
    file_name: str = Field(index=True)
    status: FileUploadStatus = Field(index=True)
    content: str
    chunk_range: list[tuple[int, int]]
