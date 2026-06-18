from __future__ import annotations

from dataclasses import dataclass

from ..errors import UnsupportedConversionError
from ..value_objects.conversion_format import normalize_format


SUPPORTED_PAIRS = {
    ("docx", "pdf"),
    ("xlsx", "pdf"),
    ("pptx", "pdf"),
    ("pdf", "docx"),
    ("csv", "xlsx"),
    ("xlsx", "csv"),
    ("png", "jpg"),
    ("jpg", "png"),
    ("jpg", "webp"),
    ("png", "webp"),
    ("mp4", "mp3"),
    ("mp4", "webm"),
    ("mov", "mp4"),
    ("wav", "mp3"),
    ("mp3", "wav"),
}


@dataclass(frozen=True)
class ConversionPolicy:
    supported_pairs: set[tuple[str, str]]

    @classmethod
    def default(cls) -> "ConversionPolicy":
        return cls(supported_pairs=SUPPORTED_PAIRS)

    def assert_supported(self, source_format: str, target_format: str) -> None:
        if (normalize_format(source_format), normalize_format(target_format)) not in self.supported_pairs:
            raise UnsupportedConversionError("Unsupported conversion format")

