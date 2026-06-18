from __future__ import annotations

from pathlib import Path

from ...core.subprocess import run_command
from ..common import expected_output


class FFmpegConverter:
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        output_path = expected_output(input_path, output_dir, target_format)
        run_command(["ffmpeg", "-y", "-i", str(input_path), str(output_path)], timeout_seconds)
        if not output_path.exists():
            raise FileNotFoundError(f"FFmpeg did not create {output_path}")
        return output_path

