from __future__ import annotations


def normalize_format(value: str | None) -> str:
    normalized = (value or "").strip().lower().lstrip(".")
    return "jpg" if normalized == "jpeg" else normalized


def extension_from_filename(filename: str) -> str:
    if "." not in filename:
        return ""
    return normalize_format(filename.rsplit(".", 1)[-1])

