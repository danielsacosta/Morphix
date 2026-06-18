from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol


class WorkspaceManager(Protocol):
    def create(self) -> AbstractContextManager[Path]:
        ...

