from __future__ import annotations

from dataclasses import dataclass

from ..errors import UnsupportedConversionError
from ..value_objects.conversion_format import normalize_format


SUPPORTED_PAIRS = {
    ("docx", "pdf"),
    ("xlsx", "pdf"),
    ("pptx", "pdf"),
    ("pdf", "docx"),
    ("pdf", "txt"),
    ("pdf", "html"),
    ("pdf", "png"),
    ("pdf", "jpg"),
    ("docx", "txt"),
    ("docx", "odt"),
    ("docx", "html"),
    ("xlsx", "ods"),
    ("pptx", "odp"),
    ("pptx", "txt"),
    ("csv", "xlsx"),
    ("xlsx", "csv"),
    ("csv", "pdf"),
    ("csv", "ods"),
    ("png", "jpg"),
    ("jpg", "png"),
    ("jpg", "webp"),
    ("png", "webp"),
    ("png", "gif"),
    ("png", "tiff"),
    ("png", "bmp"),
    ("jpg", "gif"),
    ("jpg", "tiff"),
    ("jpg", "bmp"),
    ("svg", "png"),
    ("svg", "jpg"),
    ("gif", "png"),
    ("tiff", "jpg"),
    ("mp4", "mp3"),
    ("mp4", "webm"),
    ("mov", "mp4"),
    ("avi", "mp4"),
    ("avi", "webm"),
    ("mkv", "mp4"),
    ("mkv", "webm"),
    ("mov", "webm"),
    ("m4v", "mp4"),
    ("flv", "mp4"),
    ("3gp", "mp4"),
    ("wav", "mp3"),
    ("mp3", "wav"),
    ("aac", "mp3"),
    ("flac", "mp3"),
    ("ogg", "mp3"),
    ("m4a", "mp3"),
    ("opus", "wav"),
    ("aiff", "mp3"),
    ("aiff", "wav"),
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
