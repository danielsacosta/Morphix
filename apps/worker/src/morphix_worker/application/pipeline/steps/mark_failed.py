from __future__ import annotations

from ....application.ports.jobs_repository import JobsRepository
from ....domain.entities.conversion_job import ConversionJob

FUNCTIONAL_ERROR_MESSAGE = "No fue posible convertir el archivo. Verifica que el archivo no este corrupto."


def mark_failed(repository: JobsRepository, job: ConversionJob, duration_seconds: float) -> str:
    repository.mark_failed(job.job_id, FUNCTIONAL_ERROR_MESSAGE, duration_seconds)
    return FUNCTIONAL_ERROR_MESSAGE

