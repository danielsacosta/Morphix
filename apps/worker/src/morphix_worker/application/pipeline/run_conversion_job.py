from __future__ import annotations

import time

from ..ports.converter_registry import ConverterRegistry
from ..ports.jobs_repository import JobsRepository
from ..ports.object_storage import ObjectStorage
from ..ports.workspace_manager import WorkspaceManager
from ...domain.entities.conversion_job import ConversionJob
from ...domain.entities.conversion_result import ConversionResult
from ...domain.policies.supported_conversion_policy import SupportedConversionPolicy
from ...domain.policies.timeout_policy import TimeoutPolicy
from .steps.convert_file import convert_file
from .steps.download_input import download_input
from .steps.mark_completed import mark_completed
from .steps.mark_failed import mark_failed
from .steps.mark_processing import mark_processing
from .steps.upload_output import upload_output


class ConversionJobPipeline:
    def __init__(
        self,
        storage: ObjectStorage,
        repository: JobsRepository,
        converters: ConverterRegistry,
        workspace_manager: WorkspaceManager,
        timeout_seconds: int,
        supported_conversion_policy: SupportedConversionPolicy | None = None,
    ) -> None:
        self.storage = storage
        self.repository = repository
        self.converters = converters
        self.workspace_manager = workspace_manager
        self.timeout_seconds = timeout_seconds
        self.supported_conversion_policy = supported_conversion_policy or SupportedConversionPolicy.default()

    def run(self, job: ConversionJob) -> ConversionResult:
        started_at = time.monotonic()
        mark_processing(self.repository, job)

        try:
            TimeoutPolicy(self.timeout_seconds).assert_positive()
            self.supported_conversion_policy.assert_supported(job.source_format, job.target_format)

            with self.workspace_manager.create() as workspace:
                self.repository.update_progress(job.job_id, 35, "Descargando archivo")
                input_path = download_input(self.storage, job, workspace)
                self.repository.update_progress(job.job_id, 60, "Convirtiendo archivo")
                output_path = convert_file(self.converters, job, input_path, workspace, self.timeout_seconds)
                self.repository.update_progress(job.job_id, 85, "Subiendo resultado")
                output_key = upload_output(self.storage, job, output_path)

            duration = time.monotonic() - started_at
            mark_completed(self.repository, job, output_key, duration)
            return ConversionResult(job_id=job.job_id, status="COMPLETED", output_key=output_key, error_message=None)
        except Exception:
            duration = time.monotonic() - started_at
            message = mark_failed(self.repository, job, duration)
            return ConversionResult(job_id=job.job_id, status="FAILED", output_key=job.output_key, error_message=message)
