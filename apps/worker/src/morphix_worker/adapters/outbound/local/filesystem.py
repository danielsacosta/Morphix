from __future__ import annotations

import shutil
from pathlib import Path

from ....application.ports.object_storage import ObjectStorage
from ....core.config import Settings
from ....domain.value_objects.storage_object import StorageObject


class LocalFilesystemObjectStorage(ObjectStorage):
    def __init__(self, settings: Settings) -> None:
        self._root = (Path(settings.local_data_dir) / "objects").resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, source: StorageObject) -> Path:
        path = (self._root / source.bucket / source.key).resolve()
        if path != self._root and self._root not in path.parents:
            raise ValueError("Storage key escapes local storage root")
        return path

    def download(self, source: StorageObject, destination: Path) -> None:
        source_path = self._path_for(source)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)

    def upload(self, destination: StorageObject, source: Path) -> None:
        destination_path = self._path_for(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination_path)
