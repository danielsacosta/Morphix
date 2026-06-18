from __future__ import annotations

from typing import Any

from ....domain.entities.conversion_job import ConversionJob


def load_job(payload: dict[str, Any]) -> ConversionJob:
    return ConversionJob.from_mapping(payload)

