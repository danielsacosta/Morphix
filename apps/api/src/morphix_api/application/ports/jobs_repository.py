from __future__ import annotations

from typing import Protocol

from ...domain.entities.job import Job
from ...domain.value_objects.job_status import JobStatus


class JobsRepository(Protocol):
    def put_job(self, job: Job) -> Job:
        ...

    def get_job(self, job_id: str) -> Job | None:
        ...

    def list_jobs(self, user_id: str, limit: int = 50) -> list[Job]:
        ...

    def update_job(self, job_id: str, **updates: object) -> Job:
        ...


class InMemoryJobsRepository:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}

    def put_job(self, job: Job) -> Job:
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def list_jobs(self, user_id: str, limit: int = 50) -> list[Job]:
        filtered = [job for job in self.jobs.values() if job.user_id == user_id and job.status != JobStatus.deleted]
        return sorted(filtered, key=lambda job: job.created_at, reverse=True)[:limit]

    def update_job(self, job_id: str, **updates: object) -> Job:
        from dataclasses import replace

        from ...core.time import utc_now_iso

        current = self.jobs[job_id]
        normalized_updates = {key: value for key, value in updates.items() if value is not None}
        normalized_updates["updated_at"] = utc_now_iso()
        updated = replace(current, **normalized_updates)
        self.jobs[job_id] = updated
        return updated

