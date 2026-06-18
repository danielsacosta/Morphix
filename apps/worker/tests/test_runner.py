from __future__ import annotations

from pathlib import Path

from morphix_worker.config import Settings
from morphix_worker.models import ConversionJob
from morphix_worker.runner import WorkerRunner


class FakeStorage:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, str, Path]] = []

    def download(self, bucket: str, key: str, destination: Path) -> None:
        destination.write_text("a,b\n1,2\n", encoding="utf-8")

    def upload(self, bucket: str, key: str, source: Path) -> None:
        self.uploads.append((bucket, key, source))


class FakeRepository:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def mark_processing(self, job_id: str) -> None:
        self.events.append((job_id, "PROCESSING"))

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        self.events.append((job_id, "COMPLETED"))

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        self.events.append((job_id, "FAILED"))


class FakeConverters:
    def convert(self, source_format: str, target_format: str, input_path: Path, output_dir: Path, timeout_seconds: int) -> Path:
        output = output_dir / f"input.{target_format}"
        output.write_text("converted", encoding="utf-8")
        return output


class FailingConverters:
    def convert(self, source_format: str, target_format: str, input_path: Path, output_dir: Path, timeout_seconds: int) -> Path:
        raise RuntimeError("broken")


def settings(tmp_path: Path) -> Settings:
    return Settings(
        project_name="morphix",
        environment="test",
        aws_region="us-east-1",
        jobs_table_name="jobs",
        input_bucket="input",
        output_bucket="output",
        workdir=str(tmp_path),
        conversion_timeout_seconds=30,
    )


def job() -> ConversionJob:
    return ConversionJob(
        job_id="job-1",
        user_id="user-1",
        input_bucket="input",
        input_key="input/user-1/job-1/file.csv",
        output_bucket="output",
        output_key="output/user-1/job-1/file.xlsx",
        source_format="csv",
        target_format="xlsx",
    )


def test_runner_uploads_and_marks_completed(tmp_path: Path) -> None:
    storage = FakeStorage()
    repository = FakeRepository()
    runner = WorkerRunner(settings(tmp_path), storage, repository, converters=FakeConverters())

    result = runner.run(job())

    assert result["status"] == "COMPLETED"
    assert storage.uploads[0][1] == "output/user-1/job-1/file.xlsx"
    assert repository.events == [("job-1", "PROCESSING"), ("job-1", "COMPLETED")]


def test_runner_marks_failed_on_conversion_error(tmp_path: Path) -> None:
    repository = FakeRepository()
    runner = WorkerRunner(settings(tmp_path), FakeStorage(), repository, converters=FailingConverters())

    result = runner.run(job())

    assert result["status"] == "FAILED"
    assert repository.events == [("job-1", "PROCESSING"), ("job-1", "FAILED")]

