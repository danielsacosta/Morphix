from __future__ import annotations

from ...application.ports.jobs_repository import JobsRepository
from ...domain.entities.job import Job
from ...domain.errors import JobNotFoundError, JobStateError
from ...domain.policies.ownership_policy import OwnershipPolicy
from ...domain.value_objects.job_status import JobStatus


def get_owned_job(repository: JobsRepository, job_id: str, user_id: str) -> Job:
    job = repository.get_job(job_id)
    if not job or job.status == JobStatus.deleted:
        raise JobNotFoundError("Job not found")
    OwnershipPolicy().assert_owner(job, user_id)
    return job


def assert_status(job: Job, allowed: set[JobStatus]) -> None:
    if job.status not in allowed:
        raise JobStateError(f"Cannot operate on a job in {job.status.value} status")

