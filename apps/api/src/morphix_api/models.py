from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    pending = "PENDING"
    upload_requested = "UPLOAD_REQUESTED"
    uploaded = "UPLOADED"
    processing = "PROCESSING"
    completed = "COMPLETED"
    failed = "FAILED"
    expired = "EXPIRED"
    deleted = "DELETED"


class CreateJobRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=240)
    file_size: int = Field(gt=0)
    source_format: str | None = None
    target_format: str = Field(min_length=1, max_length=16)
    content_type: str = "application/octet-stream"


class UploadUrlRequest(BaseModel):
    content_type: str = "application/octet-stream"


class JobRecord(BaseModel):
    job_id: str
    user_id: str
    input_bucket: str
    input_key: str
    output_bucket: str
    output_key: str | None = None
    source_format: str
    target_format: str
    status: JobStatus
    error_message: str | None = None
    created_at: str
    updated_at: str
    expires_at: int
    file_size: int
    duration_seconds: float | None = None
    worker_task_arn: str | None = None
    state_machine_execution_arn: str | None = None

    def to_dynamo_item(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)

    @classmethod
    def from_dynamo_item(cls, item: dict[str, Any]) -> "JobRecord":
        return cls.model_validate(item)


class JobResponse(BaseModel):
    job: JobRecord


class JobsResponse(BaseModel):
    jobs: list[JobRecord]


class UploadUrlResponse(BaseModel):
    upload_url: str
    method: str = "PUT"
    expires_in: int
    headers: dict[str, str]


class DownloadUrlResponse(BaseModel):
    download_url: str
    expires_in: int


class HealthResponse(BaseModel):
    service: str = "morphix-api"
    status: str = "ok"

