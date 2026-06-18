from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..value_objects.conversion_format import extension_from_key, normalize_format
from ..value_objects.storage_object import StorageObject


@dataclass(frozen=True)
class ConversionJob:
    job_id: str
    user_id: str
    input_object: StorageObject
    output_bucket: str
    target_format: str
    source_format: str
    output_key: str | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ConversionJob":
        input_key = str(payload["input_key"])
        source_format = normalize_format(payload.get("source_format")) or extension_from_key(input_key)
        return cls(
            job_id=str(payload["job_id"]),
            user_id=str(payload["user_id"]),
            input_object=StorageObject(bucket=str(payload["input_bucket"]), key=input_key),
            output_bucket=str(payload["output_bucket"]),
            output_key=payload.get("output_key"),
            source_format=source_format,
            target_format=normalize_format(payload["target_format"]),
        )

