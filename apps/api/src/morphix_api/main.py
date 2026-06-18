from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .aws_clients import AwsConversionGateway, ConversionGateway
from .config import Settings
from .formats import extension_from_filename, is_supported_conversion, normalize_format
from .models import (
    CreateJobRequest,
    DownloadUrlResponse,
    HealthResponse,
    JobRecord,
    JobResponse,
    JobsResponse,
    JobStatus,
    UploadUrlRequest,
    UploadUrlResponse,
)
from .repository import DynamoDBJobsRepository, JobsRepository, utc_now_iso
from .security import build_object_key, sanitize_filename

settings = Settings.from_env()
app = FastAPI(title="Morphix API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-User-Id"],
)

_repository = DynamoDBJobsRepository(settings)
_gateway = AwsConversionGateway(settings)


def get_settings() -> Settings:
    return settings


def get_repository() -> JobsRepository:
    return _repository


def get_gateway() -> ConversionGateway:
    return _gateway


def require_user_id(x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None) -> str:
    user_id = (x_user_id or "").strip()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id header is required")
    if len(user_id) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-User-Id is too long")
    return user_id


def get_owned_job(repository: JobsRepository, job_id: str, user_id: str) -> JobRecord:
    job = repository.get_job(job_id)
    if not job or job.user_id != user_id or job.status == JobStatus.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


def job_expiration_timestamp(now: datetime, settings: Settings) -> int:
    return int((now + timedelta(days=settings.job_ttl_days)).timestamp())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: CreateJobRequest,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> JobResponse:
    if payload.file_size > app_settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds the configured limit of {app_settings.max_file_size_mb} MB",
        )

    source_format = normalize_format(payload.source_format) or extension_from_filename(payload.filename)
    target_format = normalize_format(payload.target_format)
    if not is_supported_conversion(source_format, target_format):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported conversion format")

    job_id = str(uuid4())
    now = datetime.now(UTC)
    safe_filename = sanitize_filename(payload.filename)
    output_filename = f"{safe_filename.rsplit('.', 1)[0]}.{target_format}"

    job = JobRecord(
        job_id=job_id,
        user_id=user_id,
        input_bucket=app_settings.input_bucket,
        input_key=build_object_key("input", user_id, job_id, safe_filename),
        output_bucket=app_settings.output_bucket,
        output_key=build_object_key("output", user_id, job_id, output_filename),
        source_format=source_format,
        target_format=target_format,
        status=JobStatus.pending,
        created_at=now.isoformat().replace("+00:00", "Z"),
        updated_at=now.isoformat().replace("+00:00", "Z"),
        expires_at=job_expiration_timestamp(now, app_settings),
        file_size=payload.file_size,
    )
    return JobResponse(job=repository.put_job(job))


@app.get("/jobs", response_model=JobsResponse)
def list_jobs(
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobsResponse:
    return JobsResponse(jobs=repository.list_jobs(user_id=user_id))


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobResponse:
    return JobResponse(job=get_owned_job(repository, job_id, user_id))


@app.post("/jobs/{job_id}/upload-url", response_model=UploadUrlResponse)
def create_upload_url(
    job_id: str,
    payload: UploadUrlRequest,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    gateway: Annotated[ConversionGateway, Depends(get_gateway)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> UploadUrlResponse:
    job = get_owned_job(repository, job_id, user_id)
    if job.status not in {JobStatus.pending, JobStatus.upload_requested}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot upload a job in {job.status} status")

    updated = repository.update_job(job.job_id, status=JobStatus.upload_requested)
    upload_url, headers = gateway.create_upload_url(updated, payload.content_type)
    return UploadUrlResponse(upload_url=upload_url, headers=headers, expires_in=app_settings.upload_url_ttl_seconds)


@app.post("/jobs/{job_id}/start", response_model=JobResponse)
def start_job(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    gateway: Annotated[ConversionGateway, Depends(get_gateway)],
) -> JobResponse:
    job = get_owned_job(repository, job_id, user_id)
    if job.status not in {JobStatus.upload_requested, JobStatus.uploaded}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot start a job in {job.status} status")

    uploaded = repository.update_job(job.job_id, status=JobStatus.uploaded)
    execution_arn = gateway.start_conversion(uploaded)
    updated = repository.update_job(
        job.job_id,
        status=JobStatus.processing,
        state_machine_execution_arn=execution_arn,
        error_message=None,
        updated_at=utc_now_iso(),
    )
    return JobResponse(job=updated)


@app.get("/jobs/{job_id}/download-url", response_model=DownloadUrlResponse)
def create_download_url(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    gateway: Annotated[ConversionGateway, Depends(get_gateway)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> DownloadUrlResponse:
    job = get_owned_job(repository, job_id, user_id)
    if job.status != JobStatus.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not completed")

    return DownloadUrlResponse(download_url=gateway.create_download_url(job), expires_in=app_settings.download_url_ttl_seconds)


@app.delete("/jobs/{job_id}", response_model=JobResponse)
def delete_job(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobResponse:
    job = get_owned_job(repository, job_id, user_id)
    updated = repository.update_job(job.job_id, status=JobStatus.deleted)
    return JobResponse(job=updated)


handler = Mangum(app)
