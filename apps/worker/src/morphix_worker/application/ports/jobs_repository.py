from __future__ import annotations

from typing import Protocol


class JobsRepository(Protocol):
    def update_progress(self, job_id: str, progress_percent: int, progress_stage: str) -> None:
        ...

    def mark_processing(self, job_id: str) -> None:
        ...

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        ...

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        ...
