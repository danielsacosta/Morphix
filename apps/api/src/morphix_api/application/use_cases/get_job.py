from __future__ import annotations

from ...domain.entities.job import Job
from ..ports.jobs_repository import JobsRepository
from ._shared import get_owned_job


class GetJobUseCase:
    def __init__(self, repository: JobsRepository) -> None:
        self.repository = repository

    def execute(self, job_id: str, user_id: str) -> Job:
        return get_owned_job(self.repository, job_id, user_id)

