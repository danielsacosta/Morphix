from __future__ import annotations

from ....application.ports.jobs_repository import JobsRepository
from ....domain.entities.conversion_job import ConversionJob


def mark_completed(repository: JobsRepository, job: ConversionJob, output_key: str, duration_seconds: float) -> None:
    repository.mark_completed(job.job_id, output_key, duration_seconds)

