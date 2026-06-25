from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ..value_objects.job_status import JobStatus


@dataclass(frozen=True)
class Job:
    job_id: str
    user_id: str
    input_bucket: str
    input_key: str
    output_bucket: str
    source_format: str
    target_format: str
    status: JobStatus
    created_at: str
    updated_at: str
    expires_at: int
    file_size: int
    output_key: str | None = None
    error_message: str | None = None
    duration_seconds: float | None = None
    worker_task_arn: str | None = None
    state_machine_execution_arn: str | None = None
    batch_id: str | None = None
    queue_position: int | None = None
    queued_at: str | None = None
    queue_message_id: str | None = None
    progress_percent: int | None = None
    progress_stage: str | None = None

    def to_item(self) -> dict[str, Any]:
        item = asdict(self)
        item["status"] = self.status.value
        return {key: value for key, value in item.items() if value is not None}

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "Job":
        return cls(
            job_id=str(item["job_id"]),
            user_id=str(item["user_id"]),
            input_bucket=str(item["input_bucket"]),
            input_key=str(item["input_key"]),
            output_bucket=str(item["output_bucket"]),
            output_key=item.get("output_key"),
            source_format=str(item["source_format"]),
            target_format=str(item["target_format"]),
            status=JobStatus(str(item["status"])),
            error_message=item.get("error_message"),
            created_at=str(item["created_at"]),
            updated_at=str(item["updated_at"]),
            expires_at=int(item["expires_at"]),
            file_size=int(item["file_size"]),
            duration_seconds=float(item["duration_seconds"]) if item.get("duration_seconds") is not None else None,
            worker_task_arn=item.get("worker_task_arn"),
            state_machine_execution_arn=item.get("state_machine_execution_arn"),
            batch_id=item.get("batch_id"),
            queue_position=int(item["queue_position"]) if item.get("queue_position") is not None else None,
            queued_at=item.get("queued_at"),
            queue_message_id=item.get("queue_message_id"),
            progress_percent=int(item["progress_percent"]) if item.get("progress_percent") is not None else None,
            progress_stage=item.get("progress_stage"),
        )
