from __future__ import annotations

from typing import Protocol

from ...domain.entities.job import Job


class ConversionOrchestrator(Protocol):
    def start_conversion(self, job: Job) -> str:
        ...


class FakeConversionOrchestrator:
    def __init__(self) -> None:
        self.started_jobs: list[str] = []

    def start_conversion(self, job: Job) -> str:
        self.started_jobs.append(job.job_id)
        return f"arn:aws:states:us-east-1:000000000000:execution:morphix:{job.job_id}"
