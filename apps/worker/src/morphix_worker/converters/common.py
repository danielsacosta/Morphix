from __future__ import annotations

from pathlib import Path


def expected_output(input_path: Path, output_dir: Path, target_format: str) -> Path:
    extension = "jpg" if target_format == "jpeg" else target_format
    return output_dir / f"{input_path.stem}.{extension}"

