from __future__ import annotations

from typing import Protocol

from ...domain.entities.job import Job


class ObjectUrlService(Protocol):
    def create_upload_url(self, job: Job, content_type: str) -> tuple[str, dict[str, str]]:
        ...

    def create_download_url(self, job: Job) -> str:
        ...


class FakeObjectUrlService:
    def create_upload_url(self, job: Job, content_type: str) -> tuple[str, dict[str, str]]:
        return f"https://uploads.example.test/{job.input_key}", {"Content-Type": content_type}

    def create_download_url(self, job: Job) -> str:
        return f"https://downloads.example.test/{job.output_key}"

