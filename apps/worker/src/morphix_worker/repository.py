from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

import boto3

from .config import Settings


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class JobRepository(Protocol):
    def mark_processing(self, job_id: str) -> None:
        ...

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        ...

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        ...


class DynamoDBJobRepository:
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
            values[token] = value
            parts.append(f"{name} = {token}")

        self._table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET " + ", ".join(parts),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
        )

    def mark_processing(self, job_id: str) -> None:
        self._update(job_id, {"status": "PROCESSING", "error_message": None})

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        self._update(
            job_id,
            {
                "status": "COMPLETED",
                "output_key": output_key,
                "duration_seconds": round(duration_seconds, 3),
                "error_message": None,
            },
        )

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        updates: dict[str, object] = {"status": "FAILED", "error_message": error_message[:1000]}
        if duration_seconds is not None:
            updates["duration_seconds"] = round(duration_seconds, 3)
        self._update(job_id, updates)

