from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from ...domain.entities.job import Job
from ...domain.errors import BatchSizeError
from ...domain.policies.conversion_policy import ConversionPolicy
from ...domain.policies.file_size_policy import FileSizePolicy
from ..ports.jobs_repository import JobsRepository
from .create_job import CreateJobCommand, CreateJobUseCase


@dataclass(frozen=True)
class CreateBatchJobsCommand:
    user_id: str
    files: list[CreateJobCommand]


class CreateBatchJobsUseCase:
    def __init__(
        self,
        repository: JobsRepository,
        input_bucket: str,
        output_bucket: str,
        job_ttl_days: int,
        file_size_policy: FileSizePolicy,
        conversion_policy: ConversionPolicy,
        max_batch_size: int = 10,
    ) -> None:
        self.create_job = CreateJobUseCase(
            repository=repository,
            input_bucket=input_bucket,
            output_bucket=output_bucket,
            job_ttl_days=job_ttl_days,
            file_size_policy=file_size_policy,
            conversion_policy=conversion_policy,
        )
        self.max_batch_size = max_batch_size

    def execute(self, command: CreateBatchJobsCommand) -> list[Job]:
        if not command.files:
            raise BatchSizeError("Batch must include at least one file")
        if len(command.files) > self.max_batch_size:
            raise BatchSizeError(f"Batch cannot include more than {self.max_batch_size} files")

        batch_id = str(uuid4())
        jobs: list[Job] = []
        for index, file_command in enumerate(command.files, start=1):
            jobs.append(self.create_job.execute(file_command, batch_id=batch_id, queue_position=index))
        return jobs
