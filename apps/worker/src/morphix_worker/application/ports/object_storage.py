from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ...domain.value_objects.storage_object import StorageObject


class ObjectStorage(Protocol):
    def download(self, source: StorageObject, destination: Path) -> None:
        ...

    def upload(self, destination: StorageObject, source: Path) -> None:
        ...

