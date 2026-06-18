from __future__ import annotations

import json
from typing import Protocol
from uuid import uuid4

import boto3

from .config import Settings
from .models import JobRecord


class ConversionGateway(Protocol):
    def create_upload_url(self, job: JobRecord, content_type: str) -> tuple[str, dict[str, str]]:
        ...

    def create_download_url(self, job: JobRecord) -> str:
        ...

    def start_conversion(self, job: JobRecord) -> str:
        ...


class AwsConversionGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._s3 = boto3.client("s3", region_name=settings.aws_region)
        self._sfn = boto3.client("stepfunctions", region_name=settings.aws_region)

    def create_upload_url(self, job: JobRecord, content_type: str) -> tuple[str, dict[str, str]]:
        headers = {"Content-Type": content_type}
        url = self._s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": job.input_bucket,
                "Key": job.input_key,
                "ContentType": content_type,
            },
            ExpiresIn=self.settings.upload_url_ttl_seconds,
        )
        return url, headers

    def create_download_url(self, job: JobRecord) -> str:
        if not job.output_key:
            raise ValueError("Job has no output key")
        return self._s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": job.output_bucket, "Key": job.output_key},
            ExpiresIn=self.settings.download_url_ttl_seconds,
        )

    def start_conversion(self, job: JobRecord) -> str:
        if not self.settings.state_machine_arn:
            raise RuntimeError("STATE_MACHINE_ARN is required to start a conversion")

        execution_name = f"morphix-{job.job_id}-{uuid4().hex[:8]}"
        response = self._sfn.start_execution(
            stateMachineArn=self.settings.state_machine_arn,
            name=execution_name,
            input=json.dumps(job.model_dump(mode="json")),
        )
        return str(response["executionArn"])


class FakeConversionGateway:
    def __init__(self) -> None:
        self.started_jobs: list[str] = []

    def create_upload_url(self, job: JobRecord, content_type: str) -> tuple[str, dict[str, str]]:
        return f"https://uploads.example.test/{job.input_key}", {"Content-Type": content_type}

    def create_download_url(self, job: JobRecord) -> str:
        return f"https://downloads.example.test/{job.output_key}"

    def start_conversion(self, job: JobRecord) -> str:
        self.started_jobs.append(job.job_id)
        return f"arn:aws:states:us-east-1:000000000000:execution:morphix:{job.job_id}"

