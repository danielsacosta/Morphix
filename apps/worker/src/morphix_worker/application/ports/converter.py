from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Converter(Protocol):
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        ...

