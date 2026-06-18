from __future__ import annotations

from pathlib import Path

from ...core.subprocess import run_command
from ..common import expected_output


class LibreOfficePdfConverter:
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        if target_format != "pdf":
            raise ValueError("LibreOffice converter only supports PDF output")

        run_command(
            [
                "libreoffice",
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(input_path),
            ],
            timeout_seconds,
        )
        output_path = expected_output(input_path, output_dir, target_format)
        if not output_path.exists():
            raise FileNotFoundError(f"LibreOffice did not create {output_path}")
        return output_path

