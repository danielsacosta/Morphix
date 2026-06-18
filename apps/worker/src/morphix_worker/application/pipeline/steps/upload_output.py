from __future__ import annotations

from pathlib import Path

from ....application.ports.object_storage import ObjectStorage
from ....domain.entities.conversion_job import ConversionJob
from ....domain.value_objects.storage_object import StorageObject


def output_key_for(job: ConversionJob, output_path: Path) -> str:
    return job.output_key or f"output/{job.user_id}/{job.job_id}/{output_path.name}"


def upload_output(storage: ObjectStorage, job: ConversionJob, output_path: Path) -> str:
    output_key = output_key_for(job, output_path)
    storage.upload(StorageObject(bucket=job.output_bucket, key=output_key), output_path)
    return output_key

