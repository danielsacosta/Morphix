from __future__ import annotations

from ...domain.entities.job import Job
from ...domain.value_objects.job_status import JobStatus
from ..ports.jobs_repository import JobsRepository
from ._shared import get_owned_job


class DeleteJobUseCase:
    def __init__(self, repository: JobsRepository) -> None:
        self.repository = repository

    def execute(self, job_id: str, user_id: str) -> Job:
        job = get_owned_job(self.repository, job_id, user_id)
        return self.repository.update_job(job.job_id, status=JobStatus.deleted)

