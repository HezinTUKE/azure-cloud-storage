import time
import uuid

from sqlalchemy import UUID, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from application.enums.file_status import FileStatus
from application.models.base import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    file_metadata_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    path: Mapped[str] = mapped_column(String, index=True, nullable=False)
    file_size: Mapped[int] = mapped_column(Numeric, nullable=False)
    extension: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus), nullable=False, default=FileStatus.ACTIVE)
    uploaded_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()), nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()), nullable=False)
