from __future__ import annotations

import json
from uuid import uuid4

import boto3

from ....application.ports.conversion_orchestrator import ConversionOrchestrator
from ....core.config import Settings
from ....domain.entities.job import Job


class StepFunctionsConversionOrchestrator(ConversionOrchestrator):
    def __init__(self, settings: Settings):
        self.settings = settings
        self._sfn = boto3.client("stepfunctions", region_name=settings.aws_region)

    def start_conversion(self, job: Job) -> str:
        if not self.settings.state_machine_arn:
            raise RuntimeError("STATE_MACHINE_ARN is required to start a conversion")

        execution_name = f"morphix-{job.job_id}-{uuid4().hex[:8]}"
        response = self._sfn.start_execution(
            stateMachineArn=self.settings.state_machine_arn,
            name=execution_name,
            input=json.dumps(job.to_item()),
        )
        return str(response["executionArn"])
