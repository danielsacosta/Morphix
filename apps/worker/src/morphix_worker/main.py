from __future__ import annotations

from .core.config import Settings
from .entrypoints.ecs_task import run_from_env
from .entrypoints.queue_worker import run_queue_worker


def main() -> int:
    settings = Settings.from_env()
    if settings.conversion_queue_url:
        return run_queue_worker(settings)
    return run_from_env()


if __name__ == "__main__":
    raise SystemExit(main())
