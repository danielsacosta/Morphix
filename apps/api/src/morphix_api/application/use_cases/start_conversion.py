from __future__ import annotations

from ...domain.entities.job import Job
from ...domain.value_objects.job_status import JobStatus
from ...core.time import utc_now_iso
from ..ports.conversion_orchestrator import ConversionOrchestrator
from ..ports.jobs_repository import JobsRepository
from ._shared import assert_status, get_owned_job


class StartConversionUseCase:
    def __init__(self, repository: JobsRepository, orchestrator: ConversionOrchestrator) -> None:
        self.repository = repository
        self.orchestrator = orchestrator

    def execute(self, job_id: str, user_id: str) -> Job:
        job = get_owned_job(self.repository, job_id, user_id)
        assert_status(job, {JobStatus.upload_requested, JobStatus.uploaded, JobStatus.queued})
        if job.status == JobStatus.queued and job.state_machine_execution_arn:
            return job
        uploaded = self.repository.update_job(job.job_id, status=JobStatus.uploaded)
        execution_arn = self.orchestrator.start_conversion(uploaded)
        queued_at = utc_now_iso()
        return self.repository.update_job(
            uploaded.job_id,
            status=JobStatus.queued,
            state_machine_execution_arn=execution_arn,
            queued_at=queued_at,
            error_message=None,
            progress_percent=10,
            progress_stage="En cola",
        )
