from __future__ import annotations

import subprocess


def run_command(command: list[str], timeout_seconds: int) -> None:
    subprocess.run(command, check=True, timeout=timeout_seconds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

