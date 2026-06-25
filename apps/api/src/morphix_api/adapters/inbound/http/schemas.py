from __future__ import annotations

from pydantic import BaseModel, Field

from ....domain.entities.job import Job
from ....domain.value_objects.job_status import JobStatus


class CreateJobRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=240)
    file_size: int = Field(gt=0)
    source_format: str | None = None
    target_format: str = Field(min_length=1, max_length=16)
    content_type: str = "application/octet-stream"


class CreateBatchJobsRequest(BaseModel):
    files: list[CreateJobRequest] = Field(min_length=1, max_length=10)


class UploadUrlRequest(BaseModel):
    content_type: str = "application/octet-stream"


class JobSchema(BaseModel):
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
    batch_id: str | None = None
    queue_position: int | None = None
    queued_at: str | None = None
    queue_message_id: str | None = None
    progress_percent: int | None = None
    progress_stage: str | None = None

    @classmethod
    def from_domain(cls, job: Job) -> "JobSchema":
        return cls(**job.to_item())


class JobResponse(BaseModel):
    job: JobSchema


class JobsResponse(BaseModel):
    jobs: list[JobSchema]


class BatchJobsResponse(BaseModel):
    batch_id: str
    jobs: list[JobSchema]


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
