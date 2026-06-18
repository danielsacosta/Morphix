from __future__ import annotations

from ..ports.jobs_repository import JobsRepository
from ...domain.entities.job import Job


class ListJobsUseCase:
    def __init__(self, repository: JobsRepository) -> None:
        self.repository = repository

    def execute(self, user_id: str) -> list[Job]:
        return self.repository.list_jobs(user_id=user_id)

