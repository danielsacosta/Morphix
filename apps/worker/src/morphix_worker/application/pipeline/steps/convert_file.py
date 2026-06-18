from __future__ import annotations

from pathlib import Path

from ....application.ports.converter_registry import ConverterRegistry
from ....domain.entities.conversion_job import ConversionJob


def convert_file(registry: ConverterRegistry, job: ConversionJob, input_path: Path, workspace: Path, timeout_seconds: int) -> Path:
    return registry.convert(job.source_format, job.target_format, input_path, workspace, timeout_seconds)

