from __future__ import annotations

from dataclasses import dataclass

from ..errors import UnsupportedConversionError

SUPPORTED_PAIRS: set[tuple[str, str]] = {
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
class SupportedConversionPolicy:
    supported_pairs: set[tuple[str, str]]

    @classmethod
    def default(cls) -> "SupportedConversionPolicy":
        return cls(SUPPORTED_PAIRS)

    def assert_supported(self, source_format: str, target_format: str) -> None:
        if (source_format, target_format) not in self.supported_pairs:
            raise UnsupportedConversionError(f"Unsupported conversion {source_format} to {target_format}")

