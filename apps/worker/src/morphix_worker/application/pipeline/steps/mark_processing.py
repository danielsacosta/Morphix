from __future__ import annotations

from ....application.ports.jobs_repository import JobsRepository
from ....domain.entities.conversion_job import ConversionJob


def mark_processing(repository: JobsRepository, job: ConversionJob) -> None:
    repository.mark_processing(job.job_id)

