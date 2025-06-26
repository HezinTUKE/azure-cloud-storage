from sqlalchemy.orm import configure_mappers

from application.models.file_metadata import FileMetadata

from .base import Base
from .file_metadata import FileMetadata

configure_mappers()

__all__ = ["Base", "FileMetadata"]
