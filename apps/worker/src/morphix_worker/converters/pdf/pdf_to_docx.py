from __future__ import annotations

from pathlib import Path

from ..common import expected_output


class PdfToDocxConverter:
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        if target_format != "docx":
            raise ValueError("PDF converter only supports DOCX output")

        from pdf2docx import Converter as PdfConverter

        output_path = expected_output(input_path, output_dir, target_format)
        converter = PdfConverter(str(input_path))
        try:
            converter.convert(str(output_path), start=0, end=None)
        finally:
            converter.close()
        if not output_path.exists():
            raise FileNotFoundError(f"pdf2docx did not create {output_path}")
        return output_path

