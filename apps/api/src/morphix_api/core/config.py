from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    project_name: str
    environment: str
    aws_region: str
    jobs_table_name: str
    input_bucket: str
    output_bucket: str
    state_machine_arn: str
    max_file_size_mb: int
    allowed_origins: list[str]
    upload_url_ttl_seconds: int = 900
    download_url_ttl_seconds: int = 900
    job_ttl_days: int = 7
    runtime_backend: str = "aws"
    local_data_dir: str = "/var/lib/morphix"
    redis_url: str = "redis://localhost:6379/0"
    local_public_url: str = "http://localhost:8000"
    local_url_secret: str = "morphix-local-development-secret"
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
            state_machine_arn=os.getenv("STATE_MACHINE_ARN", ""),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
            allowed_origins=_split_csv(os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")),
            upload_url_ttl_seconds=int(os.getenv("UPLOAD_URL_TTL_SECONDS", "900")),
            download_url_ttl_seconds=int(os.getenv("DOWNLOAD_URL_TTL_SECONDS", "900")),
            job_ttl_days=int(os.getenv("JOB_TTL_DAYS", "7")),
            runtime_backend=os.getenv("RUNTIME_BACKEND", "aws").strip().lower(),
            local_data_dir=os.getenv("LOCAL_DATA_DIR", "/var/lib/morphix"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            local_public_url=os.getenv("LOCAL_PUBLIC_URL", "http://localhost:8000").rstrip("/"),
            local_url_secret=os.getenv("LOCAL_URL_SECRET", "morphix-local-development-secret"),
            conversion_stream=os.getenv("CONVERSION_STREAM", "morphix:conversions"),
            realtime_channel=os.getenv("REALTIME_CHANNEL", "morphix:job-events"),
        )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
