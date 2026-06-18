from __future__ import annotations

from enum import StrEnum


class JobStatus(StrEnum):
    processing = "PROCESSING"
    completed = "COMPLETED"
    failed = "FAILED"

