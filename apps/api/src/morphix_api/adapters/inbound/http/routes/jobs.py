from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from .....application.ports.conversion_orchestrator import ConversionOrchestrator
from .....application.ports.jobs_repository import JobsRepository
from .....application.ports.object_url_service import ObjectUrlService
from .....application.use_cases.create_job import CreateJobCommand, CreateJobUseCase
from .....application.use_cases.delete_job import DeleteJobUseCase
from .....application.use_cases.get_job import GetJobUseCase
from .....application.use_cases.list_jobs import ListJobsUseCase
from .....application.use_cases.request_download_url import RequestDownloadUrlUseCase
from .....application.use_cases.request_upload_url import RequestUploadUrlUseCase
from .....application.use_cases.start_conversion import StartConversionUseCase
from .....core.config import Settings
from .....domain.policies.conversion_policy import ConversionPolicy
from .....domain.policies.file_size_policy import FileSizePolicy
from ..dependencies import (
    get_conversion_orchestrator,
    get_object_url_service,
    get_repository,
    get_settings,
    require_user_id,
)
from ..schemas import (
    CreateJobRequest,
    DownloadUrlResponse,
    JobResponse,
    JobSchema,
    JobsResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: CreateJobRequest,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> JobResponse:
    use_case = CreateJobUseCase(
        repository=repository,
        input_bucket=settings.input_bucket,
        output_bucket=settings.output_bucket,
        job_ttl_days=settings.job_ttl_days,
        file_size_policy=FileSizePolicy(settings.max_file_size_bytes, settings.max_file_size_mb),
        conversion_policy=ConversionPolicy.default(),
    )
    job = use_case.execute(
        CreateJobCommand(
            user_id=user_id,
            filename=payload.filename,
            file_size=payload.file_size,
            content_type=payload.content_type,
            source_format=payload.source_format,
            target_format=payload.target_format,
        )
    )
    return JobResponse(job=JobSchema.from_domain(job))


@router.get("", response_model=JobsResponse)
def list_jobs(
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobsResponse:
    jobs = ListJobsUseCase(repository).execute(user_id)
    return JobsResponse(jobs=[JobSchema.from_domain(job) for job in jobs])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobResponse:
    job = GetJobUseCase(repository).execute(job_id, user_id)
    return JobResponse(job=JobSchema.from_domain(job))


@router.post("/{job_id}/upload-url", response_model=UploadUrlResponse)
def request_upload_url(
    job_id: str,
    payload: UploadUrlRequest,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    object_url_service: Annotated[ObjectUrlService, Depends(get_object_url_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadUrlResponse:
    result = RequestUploadUrlUseCase(repository, object_url_service).execute(job_id, user_id, payload.content_type)
    return UploadUrlResponse(upload_url=result.upload_url, headers=result.headers, expires_in=settings.upload_url_ttl_seconds)


@router.post("/{job_id}/start", response_model=JobResponse)
def start_conversion(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    orchestrator: Annotated[ConversionOrchestrator, Depends(get_conversion_orchestrator)],
) -> JobResponse:
    job = StartConversionUseCase(repository, orchestrator).execute(job_id, user_id)
    return JobResponse(job=JobSchema.from_domain(job))


@router.get("/{job_id}/download-url", response_model=DownloadUrlResponse)
def request_download_url(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
    object_url_service: Annotated[ObjectUrlService, Depends(get_object_url_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DownloadUrlResponse:
    download_url = RequestDownloadUrlUseCase(repository, object_url_service).execute(job_id, user_id)
    return DownloadUrlResponse(download_url=download_url, expires_in=settings.download_url_ttl_seconds)


@router.delete("/{job_id}", response_model=JobResponse)
def delete_job(
    job_id: str,
    user_id: Annotated[str, Depends(require_user_id)],
    repository: Annotated[JobsRepository, Depends(get_repository)],
) -> JobResponse:
    job = DeleteJobUseCase(repository).execute(job_id, user_id)
    return JobResponse(job=JobSchema.from_domain(job))

