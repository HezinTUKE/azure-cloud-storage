import time
import uuid

from pydantic import BaseModel, Field

from application.enums.file_status import FileStatus


class BaseFileMetadataDTC(BaseModel):
    file_name: str = ""
    file_size: int = 0
    extension: str = ""
    path: str = ""
    status: FileStatus = Field(default=FileStatus.ACTIVE)
    uploaded_at: int = Field(default_factory=lambda: int(time.time()))


class FileMetadataDTC(BaseFileMetadataDTC):
    file_metadata_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: int = Field(default_factory=lambda: int(time.time()))
