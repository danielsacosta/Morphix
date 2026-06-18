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
    workdir: str
    conversion_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "morphix"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            jobs_table_name=os.getenv("JOBS_TABLE_NAME", "morphix-dev-jobs"),
            input_bucket=os.getenv("INPUT_BUCKET", "morphix-dev-input"),
            output_bucket=os.getenv("OUTPUT_BUCKET", "morphix-dev-output"),
            workdir=os.getenv("WORKDIR", "/tmp/morphix"),
            conversion_timeout_seconds=int(os.getenv("CONVERSION_TIMEOUT_SECONDS", "900")),
        )

