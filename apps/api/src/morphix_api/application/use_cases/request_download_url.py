from __future__ import annotations

from ...domain.value_objects.job_status import JobStatus
from ..ports.jobs_repository import JobsRepository
from ..ports.object_url_service import ObjectUrlService
from ._shared import assert_status, get_owned_job


class RequestDownloadUrlUseCase:
    def __init__(self, repository: JobsRepository, object_url_service: ObjectUrlService) -> None:
        self.repository = repository
        self.object_url_service = object_url_service

    def execute(self, job_id: str, user_id: str) -> str:
        job = get_owned_job(self.repository, job_id, user_id)
        assert_status(job, {JobStatus.completed})
        return self.object_url_service.create_download_url(job)

