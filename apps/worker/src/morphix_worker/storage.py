from __future__ import annotations

from pathlib import Path
from typing import Protocol

import boto3

from .config import Settings


class ObjectStorage(Protocol):
    def download(self, bucket: str, key: str, destination: Path) -> None:
        ...

    def upload(self, bucket: str, key: str, source: Path) -> None:
        ...


class S3ObjectStorage:
    def __init__(self, settings: Settings) -> None:
        self._s3 = boto3.client("s3", region_name=settings.aws_region)

    def download(self, bucket: str, key: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._s3.download_file(bucket, key, str(destination))

    def upload(self, bucket: str, key: str, source: Path) -> None:
        self._s3.upload_file(str(source), bucket, key)

