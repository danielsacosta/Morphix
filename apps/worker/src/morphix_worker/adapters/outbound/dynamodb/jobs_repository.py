from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import boto3

from ....application.ports.jobs_repository import JobsRepository
from ....core.config import Settings
from ....domain.value_objects.job_status import JobStatus


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def dynamodb_value(value: object) -> object:
    if isinstance(value, JobStatus):
        return value.value
    if isinstance(value, float):
        return Decimal(str(value))
    return value


class DynamoDBJobRepository(JobsRepository):
    def __init__(self, settings: Settings) -> None:
        self._table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(settings.jobs_table_name)

    def _update(self, job_id: str, updates: dict[str, object]) -> None:
        updates["updated_at"] = utc_now_iso()
        names: dict[str, str] = {}
        values: dict[str, object] = {}
        parts: list[str] = []

        for index, (key, value) in enumerate(updates.items()):
            name = f"#n{index}"
            token = f":v{index}"
            names[name] = key
            values[token] = dynamodb_value(value)
            parts.append(f"{name} = {token}")

        self._table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET " + ", ".join(parts),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
        )

    def update_progress(self, job_id: str, progress_percent: int, progress_stage: str) -> None:
        self._update(job_id, {"progress_percent": progress_percent, "progress_stage": progress_stage})

    def mark_processing(self, job_id: str) -> None:
        self._update(
            job_id,
            {
                "status": JobStatus.processing,
                "error_message": None,
                "progress_percent": 20,
                "progress_stage": "Preparando",
            },
        )

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        self._update(
            job_id,
            {
                "status": JobStatus.completed,
                "output_key": output_key,
                "duration_seconds": round(duration_seconds, 3),
                "error_message": None,
                "progress_percent": 100,
                "progress_stage": "Completado",
            },
        )

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        updates: dict[str, object] = {
            "status": JobStatus.failed,
            "error_message": error_message[:1000],
            "progress_percent": 100,
            "progress_stage": "Fallido",
        }
        if duration_seconds is not None:
            updates["duration_seconds"] = round(duration_seconds, 3)
        self._update(job_id, updates)
