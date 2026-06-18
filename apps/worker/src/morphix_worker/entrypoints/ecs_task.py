from __future__ import annotations

import json
import os
from typing import Any

from ..adapters.outbound.dynamodb.jobs_repository import DynamoDBJobRepository
from ..adapters.outbound.s3.object_storage import S3ObjectStorage
from ..application.pipeline.run_conversion_job import ConversionJobPipeline
from ..application.pipeline.steps.load_job import load_job
from ..converters.registry import LocalConverterRegistry
from ..core.config import Settings
from ..core.logging import configure_logging
from ..core.workspace import TempWorkspaceManager


def payload_from_env() -> dict[str, Any]:
    raw_payload = os.getenv("JOB_PAYLOAD")
    if raw_payload:
        return json.loads(raw_payload)

    return {
        "job_id": os.environ["JOB_ID"],
        "user_id": os.environ["USER_ID"],
        "input_bucket": os.environ["INPUT_BUCKET"],
        "input_key": os.environ["INPUT_KEY"],
        "output_bucket": os.environ["OUTPUT_BUCKET"],
        "output_key": os.getenv("OUTPUT_KEY"),
        "source_format": os.getenv("SOURCE_FORMAT"),
        "target_format": os.environ["TARGET_FORMAT"],
    }


def run_from_env() -> int:
    configure_logging()
    settings = Settings.from_env()
    job = load_job(payload_from_env())
    pipeline = ConversionJobPipeline(
        storage=S3ObjectStorage(settings),
        repository=DynamoDBJobRepository(settings),
        converters=LocalConverterRegistry(),
        workspace_manager=TempWorkspaceManager(settings.workdir),
        timeout_seconds=settings.conversion_timeout_seconds,
    )
    result = pipeline.run(job)
    print(result.to_json())
    return 0 if result.status == "COMPLETED" else 1

