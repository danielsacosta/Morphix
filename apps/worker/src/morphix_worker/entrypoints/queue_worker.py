from __future__ import annotations

import json
import os

from ..adapters.outbound.dynamodb.jobs_repository import DynamoDBJobRepository
from ..adapters.outbound.s3.object_storage import S3ObjectStorage
from ..adapters.outbound.sqs.conversion_queue import SQSConversionQueue
from ..adapters.outbound.stepfunctions.task_callback import StepFunctionsTaskCallback
from ..application.pipeline.run_conversion_job import ConversionJobPipeline
from ..application.pipeline.steps.load_job import load_job
from ..converters.registry import LocalConverterRegistry
from ..core.config import Settings
from ..core.logging import configure_logging
from ..core.workspace import TempWorkspaceManager


def build_pipeline(settings: Settings) -> ConversionJobPipeline:
    return ConversionJobPipeline(
        storage=S3ObjectStorage(settings),
        repository=DynamoDBJobRepository(settings),
        converters=LocalConverterRegistry(),
        workspace_manager=TempWorkspaceManager(settings.workdir),
        timeout_seconds=settings.conversion_timeout_seconds,
    )


def _build_callback(settings: Settings) -> StepFunctionsTaskCallback | None:
    mode = (os.getenv("ORCHESTRATION_MODE") or "sfn").lower()
    if mode == "local":
        return None
    return StepFunctionsTaskCallback(settings)


def run_queue_worker(settings: Settings | None = None) -> int:
    configure_logging()
    resolved_settings = settings or Settings.from_env()
    if not resolved_settings.conversion_queue_url:
        raise RuntimeError("CONVERSION_QUEUE_URL is required for queue worker mode")

    queue = SQSConversionQueue(resolved_settings)
    callback = _build_callback(resolved_settings)
    pipeline = build_pipeline(resolved_settings)

    while True:
        message = queue.receive_one()
        if not message:
            continue

        envelope = json.loads(message.body)
        task_token = envelope.get("task_token")
        payload = envelope.get("payload", envelope)

        try:
            job = load_job(payload)
            result = pipeline.run(job)
        except Exception as exc:
            # The pipeline catches conversion errors internally and persists
            # FAILURE to the repository. Anything reaching here is a
            # non-conversion failure (e.g. malformed payload). In SFN mode we
            # report the failure to Step Functions; the queue message is always
            # deleted so the worker loop stays alive in local mode.
            if task_token and callback:
                callback.send_failure(str(task_token), str(exc))
            queue.delete(message)
            continue

        print(result.to_json())
        if task_token and callback:
            callback.send_result(str(task_token), result)
        queue.delete(message)
