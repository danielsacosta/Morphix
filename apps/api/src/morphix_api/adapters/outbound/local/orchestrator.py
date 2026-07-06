from __future__ import annotations

import json
import os
from uuid import uuid4

import boto3

from ....application.ports.conversion_orchestrator import ConversionOrchestrator
from ....core.config import Settings
from ....domain.entities.job import Job


class LocalSQSConversionOrchestrator(ConversionOrchestrator):
    """Bypasses Step Functions by enqueuing the job payload directly to SQS.

    In production, Step Functions owns the queued/completed/failed status
    transitions via the state machine definition. In local mode those
    transitions are persisted by:
      - the StartConversionUseCase (QUEUED, around this call)
      - the conversion pipeline (PROCESSING / COMPLETED / FAILED)
    So the local orchestrator only needs to enqueue the job payload to
    SQS, with no Step Functions task token. The worker deletes the
    message after the pipeline finishes updating DynamoDB.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        endpoint_url = os.getenv("AWS_ENDPOINT_URL") or None
        self._sqs = boto3.client("sqs", region_name=settings.aws_region, endpoint_url=endpoint_url)
        self._queue_url = os.getenv("CONVERSION_QUEUE_URL", "")

    def start_conversion(self, job: Job) -> str:
        if not self._queue_url:
            raise RuntimeError("CONVERSION_QUEUE_URL is required for local orchestration")

        payload = {
            "task_token": None,
            "payload": job.to_item(),
        }
        self._sqs.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(payload),
            MessageAttributes={
                "job_id": {"DataType": "String", "StringValue": job.job_id},
                "user_id": {"DataType": "String", "StringValue": job.user_id},
            },
        )
        return f"arn:aws:states:local:000000000000:execution:morphix-local:{job.job_id}-{uuid4().hex[:8]}"