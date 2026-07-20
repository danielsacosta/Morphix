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
        if input_path.suffix.lower() == ".svg":
            self._convert_svg(input_path, output_path, binary, timeout_seconds)
        else:
            run_command([binary, str(input_path), str(output_path)], timeout_seconds)
        if not output_path.exists():
            raise FileNotFoundError(f"ImageMagick did not create {output_path}")
        return output_path

    @staticmethod
    def _convert_svg(input_path: Path, output_path: Path, imagemagick: str, timeout_seconds: int) -> None:
        rsvg = shutil.which("rsvg-convert")
        if not rsvg:
            raise FileNotFoundError("rsvg-convert binary not found for SVG conversion")

        rasterized_path = output_path.with_name(f".{input_path.stem}.svg.png")
        try:
            run_command([rsvg, "--output", str(rasterized_path), str(input_path)], timeout_seconds)
            if output_path.suffix.lower() == ".png":
                rasterized_path.replace(output_path)
            else:
                run_command([imagemagick, str(rasterized_path), str(output_path)], timeout_seconds)
        finally:
            rasterized_path.unlink(missing_ok=True)
