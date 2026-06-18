from __future__ import annotations

from .entrypoints.ecs_task import run_from_env


def main() -> int:
    return run_from_env()


if __name__ == "__main__":
    raise SystemExit(main())

