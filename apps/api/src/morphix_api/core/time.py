from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def ttl_timestamp(now: datetime, days: int) -> int:
    return int((now + timedelta(days=days)).timestamp())

