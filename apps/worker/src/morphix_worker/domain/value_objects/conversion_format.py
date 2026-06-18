from __future__ import annotations

from pathlib import PurePath


def normalize_format(value: str | None) -> str:
    normalized = (value or "").strip().lower().lstrip(".")
    return "jpg" if normalized == "jpeg" else normalized


def extension_from_key(key: str) -> str:
    name = PurePath(key).name
    if "." not in name:
        return ""
    return normalize_format(name.rsplit(".", 1)[-1])

