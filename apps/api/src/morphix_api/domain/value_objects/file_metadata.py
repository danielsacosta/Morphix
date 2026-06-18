from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileMetadata:
    filename: str
    file_size: int
    content_type: str
    source_format: str
    target_format: str

