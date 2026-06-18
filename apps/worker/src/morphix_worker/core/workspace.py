from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator


class TempWorkspaceManager:
    def __init__(self, root: str) -> None:
        self.root = root

    @contextmanager
    def create(self) -> Iterator[Path]:
        Path(self.root).mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.root) as temp_dir:
            yield Path(temp_dir)
