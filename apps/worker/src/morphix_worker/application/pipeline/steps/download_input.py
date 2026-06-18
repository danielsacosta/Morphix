from __future__ import annotations

from pathlib import Path

from ....application.ports.object_storage import ObjectStorage
from ....domain.entities.conversion_job import ConversionJob


def download_input(storage: ObjectStorage, job: ConversionJob, workspace: Path) -> Path:
    input_path = workspace / f"input.{job.source_format}"
    storage.download(job.input_object, input_path)
    return input_path

