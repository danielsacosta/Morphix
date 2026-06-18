from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StorageObject:
    bucket: str
    key: str

