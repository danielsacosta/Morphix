from __future__ import annotations

from pathlib import Path

from ..application.ports.converter import Converter
from ..domain.policies.supported_conversion_policy import SUPPORTED_PAIRS
from .ffmpeg.media_converter import FFmpegConverter
from .imagemagick.image_converter import ImageMagickConverter
from .libreoffice.document_converter import LibreOfficeConverter
from .office.pptx_to_txt import PptxToTxtConverter
from .pdf.pdf_converter import PdfConverter
from .pdf.pdf_to_docx import PdfToDocxConverter
from .spreadsheets.csv_to_xlsx import CsvToXlsxConverter
from .spreadsheets.xlsx_to_csv import XlsxToCsvConverter


class LocalConverterRegistry:
    def __init__(self) -> None:
        libreoffice = LibreOfficeConverter()
        imagemagick = ImageMagickConverter()
        ffmpeg = FFmpegConverter()
        pdf = PdfConverter()
        self._converters: dict[tuple[str, str], Converter] = {
            ("docx", "pdf"): libreoffice,
            ("xlsx", "pdf"): libreoffice,
            ("pptx", "pdf"): libreoffice,
            ("pdf", "docx"): PdfToDocxConverter(),
            ("pdf", "txt"): pdf,
            ("pdf", "html"): pdf,
            ("pdf", "png"): pdf,
            ("pdf", "jpg"): pdf,
            ("docx", "txt"): libreoffice,
            ("docx", "odt"): libreoffice,
            ("docx", "html"): libreoffice,
            ("xlsx", "ods"): libreoffice,
            ("pptx", "odp"): libreoffice,
            ("pptx", "txt"): PptxToTxtConverter(),
            ("csv", "xlsx"): CsvToXlsxConverter(),
            ("xlsx", "csv"): XlsxToCsvConverter(),
            ("csv", "pdf"): libreoffice,
            ("csv", "ods"): libreoffice,
            ("png", "jpg"): imagemagick,
            ("jpg", "png"): imagemagick,
            ("jpg", "webp"): imagemagick,
            ("png", "webp"): imagemagick,
            ("png", "gif"): imagemagick,
            ("png", "tiff"): imagemagick,
            ("png", "bmp"): imagemagick,
            ("jpg", "gif"): imagemagick,
            ("jpg", "tiff"): imagemagick,
            ("jpg", "bmp"): imagemagick,
            ("svg", "png"): imagemagick,
            ("svg", "jpg"): imagemagick,
            ("gif", "png"): imagemagick,
            ("tiff", "jpg"): imagemagick,
            ("mp4", "mp3"): ffmpeg,
            ("mp4", "webm"): ffmpeg,
            ("mov", "mp4"): ffmpeg,
            ("avi", "mp4"): ffmpeg,
            ("avi", "webm"): ffmpeg,
            ("mkv", "mp4"): ffmpeg,
            ("mkv", "webm"): ffmpeg,
            ("mov", "webm"): ffmpeg,
            ("m4v", "mp4"): ffmpeg,
            ("flv", "mp4"): ffmpeg,
            ("3gp", "mp4"): ffmpeg,
            ("wav", "mp3"): ffmpeg,
            ("mp3", "wav"): ffmpeg,
            ("aac", "mp3"): ffmpeg,
            ("flac", "mp3"): ffmpeg,
            ("ogg", "mp3"): ffmpeg,
            ("m4a", "mp3"): ffmpeg,
            ("opus", "wav"): ffmpeg,
            ("aiff", "mp3"): ffmpeg,
            ("aiff", "wav"): ffmpeg,
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
