from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

from ..common import expected_output


class PptxToTxtConverter:
    """Extract visible slide text from a PPTX without relying on a text export filter."""

    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        del timeout_seconds
        if target_format != "txt":
            raise ValueError("PPTX text converter only supports TXT output")

        slide_names: list[str]
        with zipfile.ZipFile(input_path) as archive:
            slide_names = sorted(
                (name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=lambda name: int(re.search(r"\d+", name).group()),
            )
            slide_text = []
            for slide_name in slide_names:
                xml = archive.read(slide_name).decode("utf-8", errors="ignore")
                values = re.findall(r"<a:t[^>]*>(.*?)</a:t>", xml, flags=re.DOTALL)
                slide_text.append(" ".join(html.unescape(value) for value in values))

        output_path = expected_output(input_path, output_dir, target_format)
        output_path.write_text("\n\n".join(slide_text) + "\n", encoding="utf-8")
        if not output_path.exists():
            raise FileNotFoundError(f"PPTX text converter did not create {output_path}")
        return output_path
