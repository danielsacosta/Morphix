from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    project_name: str
    environment: str
    aws_region: str
    jobs_table_name: str
    input_bucket: str
    output_bucket: str
    conversion_queue_url: str
    workdir: str
    conversion_timeout_seconds: int
    queue_wait_time_seconds: int
    runtime_backend: str = "aws"
    local_data_dir: str = "/var/lib/morphix"
    redis_url: str = "redis://localhost:6379/0"
    conversion_stream: str = "morphix:conversions"
    realtime_channel: str = "morphix:job-events"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "morphix"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            jobs_table_name=os.getenv("JOBS_TABLE_NAME", "morphix-dev-jobs"),
            input_bucket=os.getenv("INPUT_BUCKET", "morphix-dev-input"),
            output_bucket=os.getenv("OUTPUT_BUCKET", "morphix-dev-output"),
            conversion_queue_url=os.getenv("CONVERSION_QUEUE_URL", ""),
            workdir=os.getenv("WORKDIR", "/tmp/morphix"),
            conversion_timeout_seconds=int(os.getenv("CONVERSION_TIMEOUT_SECONDS", "900")),
            queue_wait_time_seconds=int(os.getenv("QUEUE_WAIT_TIME_SECONDS", "20")),
            runtime_backend=os.getenv("RUNTIME_BACKEND", "aws").strip().lower(),
            local_data_dir=os.getenv("LOCAL_DATA_DIR", "/var/lib/morphix"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            conversion_stream=os.getenv("CONVERSION_STREAM", "morphix:conversions"),
            realtime_channel=os.getenv("REALTIME_CHANNEL", "morphix:job-events"),
        )
