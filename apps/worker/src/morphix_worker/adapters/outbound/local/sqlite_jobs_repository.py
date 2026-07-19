from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ....application.ports.jobs_repository import JobsRepository
from ....core.config import Settings
from ....domain.value_objects.job_status import JobStatus


JOB_COLUMNS = (
    "job_id", "user_id", "input_bucket", "input_key", "output_bucket", "output_key",
    "source_format", "target_format", "status", "created_at", "updated_at", "expires_at",
    "file_size", "error_message", "duration_seconds", "worker_task_arn",
    "state_machine_execution_arn", "batch_id", "queue_position", "queued_at",
    "queue_message_id", "progress_percent", "progress_stage",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    input_bucket TEXT NOT NULL,
    input_key TEXT NOT NULL,
    output_bucket TEXT NOT NULL,
    output_key TEXT,
    source_format TEXT NOT NULL,
    target_format TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    file_size INTEGER NOT NULL,
    error_message TEXT,
    duration_seconds REAL,
    worker_task_arn TEXT,
    state_machine_execution_arn TEXT,
    batch_id TEXT,
    queue_position INTEGER,
    queued_at TEXT,
    queue_message_id TEXT,
    progress_percent INTEGER,
    progress_stage TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_user_created ON jobs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_user_batch ON jobs(user_id, batch_id);
"""


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class SQLiteJobRepository(JobsRepository):
    def __init__(self, settings: Settings) -> None:
        self._db_path = Path(settings.local_data_dir) / "morphix.sqlite"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._redis_url = settings.redis_url
        self._realtime_channel = settings.realtime_channel
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.executescript(SCHEMA)

    def _row(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return {column: row[column] for column in JOB_COLUMNS if row[column] is not None} if row else None

    def _publish(self, job: dict[str, Any]) -> None:
        try:
            from redis import Redis

            fields = {column: job[column] for column in JOB_COLUMNS if column in job}
            Redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            ).publish(
                self._realtime_channel,
                json.dumps({"type": "job.updated", "job": fields}, separators=(",", ":")),
            )
        except Exception:
            return

    def _update(self, job_id: str, updates: dict[str, object]) -> None:
        normalized = {
            key: value.value if isinstance(value, JobStatus) else value
            for key, value in updates.items()
            if key in JOB_COLUMNS and key != "job_id"
        }
        normalized["updated_at"] = utc_now_iso()
        assignments = ", ".join(f"{key} = ?" for key in normalized)
        with self._connect() as connection:
            cursor = connection.execute(
                f"UPDATE jobs SET {assignments} WHERE job_id = ?",
                [*normalized.values(), job_id],
            )
            if cursor.rowcount == 0:
                raise KeyError(job_id)
        job = self._row(job_id)
        if job:
            self._publish(job)

    def update_progress(self, job_id: str, progress_percent: int, progress_stage: str) -> None:
        self._update(job_id, {"progress_percent": progress_percent, "progress_stage": progress_stage})

    def mark_processing(self, job_id: str) -> None:
        self._update(job_id, {
            "status": JobStatus.processing,
            "error_message": None,
            "progress_percent": 20,
            "progress_stage": "Preparando",
        })

    def mark_completed(self, job_id: str, output_key: str, duration_seconds: float) -> None:
        self._update(job_id, {
            "status": JobStatus.completed,
            "output_key": output_key,
            "duration_seconds": round(duration_seconds, 3),
            "error_message": None,
            "progress_percent": 100,
            "progress_stage": "Completado",
        })

    def mark_failed(self, job_id: str, error_message: str, duration_seconds: float | None = None) -> None:
        updates: dict[str, object] = {
            "status": JobStatus.failed,
            "error_message": error_message[:1000],
            "progress_percent": 100,
            "progress_stage": "Fallido",
        }
        if duration_seconds is not None:
            updates["duration_seconds"] = round(duration_seconds, 3)
        self._update(job_id, updates)
