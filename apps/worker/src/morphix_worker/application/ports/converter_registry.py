from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ConverterRegistry(Protocol):
    @property
    def supported_pairs(self) -> set[tuple[str, str]]:
        ...

    def convert(self, source_format: str, target_format: str, input_path: Path, output_dir: Path, timeout_seconds: int) -> Path:
        ...

