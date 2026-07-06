from __future__ import annotations

import os
from urllib.parse import urlsplit, urlunsplit

import boto3

from ....application.ports.object_url_service import ObjectUrlService
from ....core.config import Settings
from ....domain.entities.job import Job


class S3PresignedUrlService(ObjectUrlService):
    def __init__(self, settings: Settings):
        self.settings = settings
        self._s3 = boto3.client("s3", region_name=settings.aws_region)
        # Optional (local only): rewrite the host of generated presigned URLs so
        # the browser can reach LocalStack from the host. When unset (production),
        # presigned URLs are returned untouched.
        self._browser_url_base = (os.getenv("S3_BROWSER_URL_BASE") or "").strip() or None

    def _for_browser(self, url: str) -> str:
        if not self._browser_url_base:
            return url
        parts = urlsplit(url)
        base_parts = urlsplit(self._browser_url_base)
        return urlunsplit((base_parts.scheme or parts.scheme, base_parts.netloc, parts.path, parts.query, parts.fragment))

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
        return self._for_browser(url), headers

    def create_download_url(self, job: Job) -> str:
        url = self._s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": job.output_bucket, "Key": job.output_key},
            ExpiresIn=self.settings.download_url_ttl_seconds,
        )
        return self._for_browser(url)

