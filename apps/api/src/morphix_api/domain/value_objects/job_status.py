from __future__ import annotations

from enum import StrEnum


class JobStatus(StrEnum):
    pending = "PENDING"
    upload_requested = "UPLOAD_REQUESTED"
    uploaded = "UPLOADED"
    queued = "QUEUED"
    processing = "PROCESSING"
    completed = "COMPLETED"
    failed = "FAILED"
    expired = "EXPIRED"
    deleted = "DELETED"

    @property
    def is_active(self) -> bool:
        return self in {
            JobStatus.pending,
            JobStatus.upload_requested,
            JobStatus.uploaded,
            JobStatus.queued,
            JobStatus.processing,
        }
