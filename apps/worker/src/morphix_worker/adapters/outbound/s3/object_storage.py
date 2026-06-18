from __future__ import annotations

from pathlib import Path

import boto3

from ....application.ports.object_storage import ObjectStorage
from ....core.config import Settings
from ....domain.value_objects.storage_object import StorageObject


class S3ObjectStorage(ObjectStorage):
    def __init__(self, settings: Settings) -> None:
        self._s3 = boto3.client("s3", region_name=settings.aws_region)

    def download(self, source: StorageObject, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._s3.download_file(source.bucket, source.key, str(destination))

    def upload(self, destination: StorageObject, source: Path) -> None:
        self._s3.upload_file(str(source), destination.bucket, destination.key)

