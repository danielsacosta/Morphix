from __future__ import annotations

import re
from pathlib import PurePath

SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    base_name = PurePath(filename).name.strip()
    cleaned = SAFE_CHARS.sub("-", base_name).strip(".-")
    return cleaned[:180] or "upload"


def build_object_key(prefix: str, user_id: str, job_id: str, filename: str) -> str:
    safe_user = SAFE_CHARS.sub("-", user_id)[:120]
    return f"{prefix}/{safe_user}/{job_id}/{sanitize_filename(filename)}"

