from __future__ import annotations

from pathlib import Path

from ...core.subprocess import run_command
from ..common import expected_output


class LibreOfficeConverter:
    """Convert office-compatible files through LibreOffice headless filters."""

    _FILTERS = {
        "pdf": "pdf",
        "txt": "txt:Text",
        "html": "html:XHTML Writer File",
        "odt": "odt",
        "ods": "ods",
        "odp": "odp",
    }

    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        conversion_filter = self._FILTERS.get(target_format)
        if conversion_filter is None:
            raise ValueError(f"LibreOffice does not support {target_format} output")

        run_command(
            [
                "libreoffice",
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to",
                conversion_filter,
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
