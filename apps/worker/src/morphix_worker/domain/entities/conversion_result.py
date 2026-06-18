from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ConversionResult:
    job_id: str
    status: str
    output_key: str | None
    error_message: str | None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True, sort_keys=True)

