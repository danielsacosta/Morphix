from __future__ import annotations

from pathlib import Path

from ..application.ports.converter import Converter
from ..domain.policies.supported_conversion_policy import SUPPORTED_PAIRS
from .ffmpeg.media_converter import FFmpegConverter
from .imagemagick.image_converter import ImageMagickConverter
from .libreoffice.document_to_pdf import LibreOfficePdfConverter
from .pdf.pdf_to_docx import PdfToDocxConverter
from .spreadsheets.csv_to_xlsx import CsvToXlsxConverter
from .spreadsheets.xlsx_to_csv import XlsxToCsvConverter


class LocalConverterRegistry:
    def __init__(self) -> None:
        libreoffice = LibreOfficePdfConverter()
        imagemagick = ImageMagickConverter()
        ffmpeg = FFmpegConverter()
        self._converters: dict[tuple[str, str], Converter] = {
            ("docx", "pdf"): libreoffice,
            ("xlsx", "pdf"): libreoffice,
            ("pptx", "pdf"): libreoffice,
            ("pdf", "docx"): PdfToDocxConverter(),
            ("csv", "xlsx"): CsvToXlsxConverter(),
            ("xlsx", "csv"): XlsxToCsvConverter(),
            ("png", "jpg"): imagemagick,
            ("jpg", "png"): imagemagick,
            ("jpg", "webp"): imagemagick,
            ("png", "webp"): imagemagick,
            ("mp4", "mp3"): ffmpeg,
            ("mp4", "webm"): ffmpeg,
            ("mov", "mp4"): ffmpeg,
            ("wav", "mp3"): ffmpeg,
            ("mp3", "wav"): ffmpeg,
        }

    @property
    def supported_pairs(self) -> set[tuple[str, str]]:
        return set(self._converters)

    def convert(self, source_format: str, target_format: str, input_path: Path, output_dir: Path, timeout_seconds: int) -> Path:
        converter = self._converters.get((source_format, target_format))
        if not converter:
            raise ValueError(f"Unsupported conversion {source_format} to {target_format}")
        return converter.convert(input_path, output_dir, target_format, timeout_seconds)


ConverterRegistry = LocalConverterRegistry

assert SUPPORTED_PAIRS == LocalConverterRegistry().supported_pairs

