from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities.job import Job
from ...domain.value_objects.job_status import JobStatus
from ..ports.jobs_repository import JobsRepository
from ..ports.object_url_service import ObjectUrlService
from ._shared import assert_status, get_owned_job


@dataclass(frozen=True)
class UploadUrlResult:
    job: Job
    upload_url: str
    headers: dict[str, str]


class RequestUploadUrlUseCase:
    def __init__(self, repository: JobsRepository, object_url_service: ObjectUrlService) -> None:
        self.repository = repository
        self.object_url_service = object_url_service

    def execute(self, job_id: str, user_id: str, content_type: str) -> UploadUrlResult:
        job = get_owned_job(self.repository, job_id, user_id)
        assert_status(job, {JobStatus.pending, JobStatus.upload_requested})
        updated = self.repository.update_job(job.job_id, status=JobStatus.upload_requested)
        upload_url, headers = self.object_url_service.create_upload_url(updated, content_type)
        return UploadUrlResult(job=updated, upload_url=upload_url, headers=headers)

