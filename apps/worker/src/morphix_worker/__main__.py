from __future__ import annotations

import sys

from .config import Settings
from .models import ConversionJob
from .repository import DynamoDBJobRepository
from .runner import WorkerRunner, format_result
from .storage import S3ObjectStorage


def main() -> int:
    settings = Settings.from_env()
    job = ConversionJob.from_env()
    runner = WorkerRunner(settings=settings, storage=S3ObjectStorage(settings), repository=DynamoDBJobRepository(settings))
    result = runner.run(job)
    print(format_result(result))
    return 0 if result["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

