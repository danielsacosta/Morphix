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
        )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
