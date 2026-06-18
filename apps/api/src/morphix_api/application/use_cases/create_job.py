from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from ...core.security import build_object_key, sanitize_filename
from ...core.time import ttl_timestamp, utc_now
from ...domain.entities.job import Job
from ...domain.policies.conversion_policy import ConversionPolicy
from ...domain.policies.file_size_policy import FileSizePolicy
from ...domain.value_objects.conversion_format import extension_from_filename, normalize_format
from ...domain.value_objects.job_status import JobStatus
from ..ports.jobs_repository import JobsRepository


@dataclass(frozen=True)
class CreateJobCommand:
    user_id: str
    filename: str
    file_size: int
    content_type: str
    source_format: str | None
    target_format: str


class CreateJobUseCase:
    def __init__(
        self,
        repository: JobsRepository,
        input_bucket: str,
        output_bucket: str,
        job_ttl_days: int,
        file_size_policy: FileSizePolicy,
        conversion_policy: ConversionPolicy,
    ) -> None:
        self.repository = repository
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        self.job_ttl_days = job_ttl_days
        self.file_size_policy = file_size_policy
        self.conversion_policy = conversion_policy

    def execute(self, command: CreateJobCommand) -> Job:
        self.file_size_policy.assert_allowed(command.file_size)
        source_format = normalize_format(command.source_format) or extension_from_filename(command.filename)
        target_format = normalize_format(command.target_format)
        self.conversion_policy.assert_supported(source_format, target_format)

        job_id = str(uuid4())
        now = utc_now()
        now_iso = now.isoformat().replace("+00:00", "Z")
        safe_filename = sanitize_filename(command.filename)
        output_filename = f"{safe_filename.rsplit('.', 1)[0]}.{target_format}"

        job = Job(
            job_id=job_id,
            user_id=command.user_id,
            input_bucket=self.input_bucket,
            input_key=build_object_key("input", command.user_id, job_id, safe_filename),
            output_bucket=self.output_bucket,
            output_key=build_object_key("output", command.user_id, job_id, output_filename),
            source_format=source_format,
            target_format=target_format,
            status=JobStatus.pending,
            created_at=now_iso,
            updated_at=now_iso,
            expires_at=ttl_timestamp(now, self.job_ttl_days),
            file_size=command.file_size,
        )
        return self.repository.put_job(job)

