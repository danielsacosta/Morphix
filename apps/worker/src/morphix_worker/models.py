from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any


def normalize_format(value: str | None) -> str:
    normalized = (value or "").strip().lower().lstrip(".")
    return "jpg" if normalized == "jpeg" else normalized


def extension_from_key(key: str) -> str:
    name = PurePath(key).name
    if "." not in name:
        return ""
    return normalize_format(name.rsplit(".", 1)[-1])


@dataclass(frozen=True)
class ConversionJob:
    job_id: str
    user_id: str
    input_bucket: str
    input_key: str
    output_bucket: str
    target_format: str
    source_format: str
    output_key: str | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ConversionJob":
        input_key = str(payload["input_key"])
        source_format = normalize_format(payload.get("source_format")) or extension_from_key(input_key)
        target_format = normalize_format(payload["target_format"])
        return cls(
            job_id=str(payload["job_id"]),
            user_id=str(payload["user_id"]),
            input_bucket=str(payload["input_bucket"]),
            input_key=input_key,
            output_bucket=str(payload["output_bucket"]),
            output_key=payload.get("output_key"),
            source_format=source_format,
            target_format=target_format,
        )

    @classmethod
    def from_env(cls) -> "ConversionJob":
        raw_payload = os.getenv("JOB_PAYLOAD")
        if raw_payload:
            return cls.from_mapping(json.loads(raw_payload))

        payload = {
            "job_id": os.environ["JOB_ID"],
            "user_id": os.environ["USER_ID"],
            "input_bucket": os.environ["INPUT_BUCKET"],
            "input_key": os.environ["INPUT_KEY"],
            "output_bucket": os.environ["OUTPUT_BUCKET"],
            "output_key": os.getenv("OUTPUT_KEY"),
            "source_format": os.getenv("SOURCE_FORMAT"),
            "target_format": os.environ["TARGET_FORMAT"],
        }
        return cls.from_mapping(payload)

