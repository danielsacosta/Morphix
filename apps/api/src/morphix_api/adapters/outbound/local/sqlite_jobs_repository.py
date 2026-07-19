from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ....application.ports.jobs_repository import JobsRepository
from ....core.config import Settings
from ....core.time import utc_now_iso
from ....domain.entities.job import Job
from ....domain.value_objects.job_status import JobStatus


JOB_COLUMNS = (
    "job_id",
    "user_id",
    "input_bucket",
    "input_key",
    "output_bucket",
    "output_key",
    "source_format",
    "target_format",
    "status",
    "created_at",
    "updated_at",
    "expires_at",
    "file_size",
    "error_message",
    "duration_seconds",
    "worker_task_arn",
    "state_machine_execution_arn",
    "batch_id",
    "queue_position",
    "queued_at",
    "queue_message_id",
    "progress_percent",
    "progress_stage",
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


class SQLiteJobsRepository(JobsRepository):
    """SQLite implementation of the API jobs port for local development."""

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

    @staticmethod
    def _item_from_row(row: sqlite3.Row) -> dict[str, Any]:
        return {column: row[column] for column in JOB_COLUMNS if row[column] is not None}

    def _publish(self, job: Job) -> None:
        try:
            from redis import Redis

            Redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            ).publish(
                self._realtime_channel,
                json.dumps({"type": "job.updated", "job": job.to_item()}, separators=(",", ":")),
            )
        except Exception:
            # Realtime is an enhancement; persistence must remain available.
            return

    def put_job(self, job: Job) -> Job:
        item = job.to_item()
        values = [item.get(column) for column in JOB_COLUMNS]
        placeholders = ", ".join("?" for _ in JOB_COLUMNS)
        columns = ", ".join(JOB_COLUMNS)
        with self._connect() as connection:
            connection.execute(
                f"INSERT OR REPLACE INTO jobs ({columns}) VALUES ({placeholders})",
                values,
            )
        self._publish(job)
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return Job.from_item(self._item_from_row(row)) if row else None

    def list_jobs(self, user_id: str, limit: int = 50, batch_id: str | None = None) -> list[Job]:
        query = "SELECT * FROM jobs WHERE user_id = ? AND status != ?"
        params: list[object] = [user_id, JobStatus.deleted.value]
        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Job.from_item(self._item_from_row(row)) for row in rows]

    def update_job(self, job_id: str, **updates: object) -> Job:
        allowed = set(JOB_COLUMNS) - {"job_id"}
        updates = {key: value for key, value in updates.items() if key in allowed}
        if not updates:
            current = self.get_job(job_id)
            if current is None:
                raise KeyError(job_id)
            return current

        updates["updated_at"] = utc_now_iso()
        normalized = {key: value.value if isinstance(value, JobStatus) else value for key, value in updates.items()}
        assignments = ", ".join(f"{key} = ?" for key in normalized)
        with self._connect() as connection:
            cursor = connection.execute(
                f"UPDATE jobs SET {assignments} WHERE job_id = ?",
                [*normalized.values(), job_id],
            )
            if cursor.rowcount == 0:
                raise KeyError(job_id)

        updated = self.get_job(job_id)
        if updated is None:
            raise KeyError(job_id)
        self._publish(updated)
        return updated
