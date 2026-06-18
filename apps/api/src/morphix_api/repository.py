from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

import boto3
from boto3.dynamodb.conditions import Key

from .config import Settings
from .models import JobRecord, JobStatus


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class JobsRepository(Protocol):
    def put_job(self, job: JobRecord) -> JobRecord:
        ...

    def get_job(self, job_id: str) -> JobRecord | None:
        ...

    def list_jobs(self, user_id: str, limit: int = 50) -> list[JobRecord]:
        ...

    def update_job(self, job_id: str, **updates: object) -> JobRecord:
        ...


class DynamoDBJobsRepository:
    def __init__(self, settings: Settings):
        self._table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(settings.jobs_table_name)

    def put_job(self, job: JobRecord) -> JobRecord:
        self._table.put_item(Item=job.to_dynamo_item())
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        response = self._table.get_item(Key={"job_id": job_id})
        item = response.get("Item")
        return JobRecord.from_dynamo_item(item) if item else None

    def list_jobs(self, user_id: str, limit: int = 50) -> list[JobRecord]:
        response = self._table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        return [JobRecord.from_dynamo_item(item) for item in response.get("Items", [])]

    def update_job(self, job_id: str, **updates: object) -> JobRecord:
        updates = {key: value for key, value in updates.items() if value is not None}
        updates["updated_at"] = utc_now_iso()

        expression_parts: list[str] = []
        attribute_names: dict[str, str] = {}
        attribute_values: dict[str, object] = {}

        for index, (key, value) in enumerate(updates.items()):
            name_token = f"#n{index}"
            value_token = f":v{index}"
            attribute_names[name_token] = key
            attribute_values[value_token] = value.value if isinstance(value, JobStatus) else value
            expression_parts.append(f"{name_token} = {value_token}")

        response = self._table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET " + ", ".join(expression_parts),
            ExpressionAttributeNames=attribute_names,
            ExpressionAttributeValues=attribute_values,
            ReturnValues="ALL_NEW",
        )
        return JobRecord.from_dynamo_item(response["Attributes"])


class InMemoryJobsRepository:
    def __init__(self) -> None:
        self.jobs: dict[str, JobRecord] = {}

    def put_job(self, job: JobRecord) -> JobRecord:
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        return self.jobs.get(job_id)

    def list_jobs(self, user_id: str, limit: int = 50) -> list[JobRecord]:
        filtered = [job for job in self.jobs.values() if job.user_id == user_id and job.status != JobStatus.deleted]
        return sorted(filtered, key=lambda job: job.created_at, reverse=True)[:limit]

    def update_job(self, job_id: str, **updates: object) -> JobRecord:
        current = self.jobs[job_id]
        payload = current.model_dump()
        for key, value in updates.items():
            if value is not None:
                payload[key] = value
        payload["updated_at"] = utc_now_iso()
        updated = JobRecord.model_validate(payload)
        self.jobs[job_id] = updated
        return updated

