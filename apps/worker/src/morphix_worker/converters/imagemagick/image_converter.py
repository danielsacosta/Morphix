from __future__ import annotations

import shutil
from pathlib import Path

from ...core.subprocess import run_command
from ..common import expected_output


class ImageMagickConverter:
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        binary = shutil.which("magick") or shutil.which("convert")
        if not binary:
            raise FileNotFoundError("ImageMagick binary not found")

        output_path = expected_output(input_path, output_dir, target_format)
        run_command([binary, str(input_path), str(output_path)], timeout_seconds)
        if not output_path.exists():
            raise FileNotFoundError(f"ImageMagick did not create {output_path}")
        return output_path

