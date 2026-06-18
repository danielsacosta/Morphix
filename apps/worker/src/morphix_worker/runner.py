from __future__ import annotations

import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from .config import Settings
from .converters import ConverterRegistry
from .models import ConversionJob
from .repository import JobRepository
from .storage import ObjectStorage


class WorkerRunner:
    def __init__(
        self,
        settings: Settings,
        storage: ObjectStorage,
        repository: JobRepository,
        converters: ConverterRegistry | None = None,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.repository = repository
        self.converters = converters or ConverterRegistry()

    def run(self, job: ConversionJob) -> dict[str, str | float | None]:
        started_at = time.monotonic()
        self.repository.mark_processing(job.job_id)

        try:
            with TemporaryDirectory(dir=self.settings.workdir) as temp_dir:
                workspace = Path(temp_dir)
                input_path = workspace / f"input.{job.source_format}"
                self.storage.download(job.input_bucket, job.input_key, input_path)

                output_path = self.converters.convert(
                    job.source_format,
                    job.target_format,
                    input_path,
                    workspace,
                    self.settings.conversion_timeout_seconds,
                )
                output_key = job.output_key or f"output/{job.user_id}/{job.job_id}/{output_path.name}"
                self.storage.upload(job.output_bucket, output_key, output_path)

            duration = time.monotonic() - started_at
            self.repository.mark_completed(job.job_id, output_key, duration)
            return {"job_id": job.job_id, "status": "COMPLETED", "output_key": output_key, "error_message": None}
        except Exception as exc:
            duration = time.monotonic() - started_at
            message = "No fue posible convertir el archivo. Verifica que el archivo no este corrupto."
            self.repository.mark_failed(job.job_id, message, duration)
            return {"job_id": job.job_id, "status": "FAILED", "output_key": job.output_key, "error_message": message}


def format_result(result: dict[str, str | float | None]) -> str:
    return json.dumps(result, ensure_ascii=True, sort_keys=True)

