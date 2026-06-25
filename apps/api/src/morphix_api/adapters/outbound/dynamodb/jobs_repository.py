from __future__ import annotations

import boto3
from boto3.dynamodb.conditions import Key

from ....application.ports.jobs_repository import JobsRepository
from ....core.config import Settings
from ....core.time import utc_now_iso
from ....domain.entities.job import Job
from ....domain.value_objects.job_status import JobStatus


class DynamoDBJobsRepository(JobsRepository):
    def __init__(self, settings: Settings):
        self._table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(settings.jobs_table_name)

    def put_job(self, job: Job) -> Job:
        self._table.put_item(Item=job.to_item())
        return job

    def get_job(self, job_id: str) -> Job | None:
        response = self._table.get_item(Key={"job_id": job_id})
        item = response.get("Item")
        return Job.from_item(item) if item else None

    def list_jobs(self, user_id: str, limit: int = 50, batch_id: str | None = None) -> list[Job]:
        response = self._table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        jobs = [Job.from_item(item) for item in response.get("Items", [])]
        jobs = [job for job in jobs if job.status != JobStatus.deleted]
        if batch_id:
            jobs = [job for job in jobs if job.batch_id == batch_id]
        return jobs

    def update_job(self, job_id: str, **updates: object) -> Job:
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
        return Job.from_item(response["Attributes"])
