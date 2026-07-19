from __future__ import annotations

from pathlib import Path


class LocalFilesystemStorage:
    def __init__(self, root_dir: str) -> None:
        self._root = Path(root_dir) / "objects"
        self._root.mkdir(parents=True, exist_ok=True)

    def path_for(self, bucket: str, key: str) -> Path:
        root = self._root.resolve()
        path = (root / bucket / key).resolve()
        if path != root and root not in path.parents:
            raise ValueError("Storage key escapes local storage root")
        return path
