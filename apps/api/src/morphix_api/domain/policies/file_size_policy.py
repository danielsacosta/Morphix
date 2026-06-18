from __future__ import annotations

from dataclasses import dataclass

from ..errors import FileTooLargeError


@dataclass(frozen=True)
class FileSizePolicy:
    max_size_bytes: int
    max_size_mb: int

    def assert_allowed(self, file_size: int) -> None:
        if file_size > self.max_size_bytes:
            raise FileTooLargeError(f"File exceeds the configured limit of {self.max_size_mb} MB")

