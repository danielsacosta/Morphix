from __future__ import annotations

import html
from pathlib import Path

from ..common import expected_output


class PdfConverter:
    """Convert a PDF to text, HTML or a raster image.

    The worker currently produces one output artifact per job, so PDF image
    conversions render the first page. Text and HTML conversions include all
    pages.
    """

    _IMAGE_TARGETS = {"png", "jpg"}
    _TEXT_TARGETS = {"txt", "html"}

    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        del timeout_seconds
        if target_format not in self._IMAGE_TARGETS | self._TEXT_TARGETS:
            raise ValueError(f"PDF converter does not support {target_format} output")

        import fitz

        output_path = expected_output(input_path, output_dir, target_format)
        document = fitz.open(str(input_path))
        try:
            if target_format == "txt":
                output_path.write_text("\n\n".join(page.get_text() for page in document), encoding="utf-8")
            elif target_format == "html":
                pages = "\n".join(
                    f'<section data-page="{index + 1}"><pre>{html.escape(page.get_text())}</pre></section>'
                    for index, page in enumerate(document)
                )
                output_path.write_text(
                    "<!doctype html><html><head><meta charset=\"utf-8\"><title>"
                    f"{html.escape(input_path.stem)}</title></head><body>{pages}</body></html>",
                    encoding="utf-8",
                )
            else:
                if len(document) == 0:
                    raise ValueError("PDF does not contain any pages")
                pixmap = document[0].get_pixmap(dpi=150, alpha=False)
                pixmap.save(str(output_path))
        finally:
            document.close()

        if not output_path.exists():
            raise FileNotFoundError(f"PyMuPDF did not create {output_path}")
        return output_path
