from __future__ import annotations

import boto3

from ....core.config import Settings
from ....domain.entities.conversion_result import ConversionResult


class StepFunctionsTaskCallback:
    def __init__(self, settings: Settings) -> None:
        self._sfn = boto3.client("stepfunctions", region_name=settings.aws_region)

    def send_result(self, task_token: str, result: ConversionResult) -> None:
        if result.status == "COMPLETED":
            self._sfn.send_task_success(taskToken=task_token, output=result.to_json())
            return

        self.send_failure(task_token, result.error_message or "The conversion worker failed.")

    def send_failure(self, task_token: str, cause: str) -> None:
        self._sfn.send_task_failure(taskToken=task_token, error="WorkerFailed", cause=cause[:32768])
