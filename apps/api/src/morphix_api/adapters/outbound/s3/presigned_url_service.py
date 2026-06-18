from __future__ import annotations

import boto3

from ....application.ports.object_url_service import ObjectUrlService
from ....core.config import Settings
from ....domain.entities.job import Job


class S3PresignedUrlService(ObjectUrlService):
    def __init__(self, settings: Settings):
        self.settings = settings
        self._s3 = boto3.client("s3", region_name=settings.aws_region)

    def create_upload_url(self, job: Job, content_type: str) -> tuple[str, dict[str, str]]:
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

    def create_download_url(self, job: Job) -> str:
        return self._s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": job.output_bucket, "Key": job.output_key},
            ExpiresIn=self.settings.download_url_ttl_seconds,
        )

