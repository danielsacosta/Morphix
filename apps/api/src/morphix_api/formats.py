from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Conversion:
    source: str
    target: str
    engine: str
    category: str


SUPPORTED_CONVERSIONS: tuple[Conversion, ...] = (
    Conversion("docx", "pdf", "LibreOffice", "documents"),
    Conversion("xlsx", "pdf", "LibreOffice", "documents"),
    Conversion("pptx", "pdf", "LibreOffice", "documents"),
    Conversion("pdf", "docx", "pdf2docx/PyMuPDF", "documents"),
    Conversion("csv", "xlsx", "openpyxl", "documents"),
    Conversion("xlsx", "csv", "openpyxl", "documents"),
    Conversion("png", "jpg", "ImageMagick", "images"),
    Conversion("jpg", "png", "ImageMagick", "images"),
    Conversion("jpg", "webp", "ImageMagick", "images"),
    Conversion("png", "webp", "ImageMagick", "images"),
    Conversion("mp4", "mp3", "FFmpeg", "media"),
    Conversion("mp4", "webm", "FFmpeg", "media"),
    Conversion("mov", "mp4", "FFmpeg", "media"),
    Conversion("wav", "mp3", "FFmpeg", "media"),
    Conversion("mp3", "wav", "FFmpeg", "media"),
)

SUPPORTED_PAIRS = {(item.source, item.target) for item in SUPPORTED_CONVERSIONS}


def normalize_format(value: str | None) -> str:
    normalized = (value or "").strip().lower().lstrip(".")
    return "jpg" if normalized == "jpeg" else normalized


def extension_from_filename(filename: str) -> str:
    if "." not in filename:
        return ""
    return normalize_format(filename.rsplit(".", 1)[-1])


def is_supported_conversion(source: str, target: str) -> bool:
    return (normalize_format(source), normalize_format(target)) in SUPPORTED_PAIRS


def conversion_for(source: str, target: str) -> Conversion | None:
    source = normalize_format(source)
    target = normalize_format(target)
    return next((item for item in SUPPORTED_CONVERSIONS if item.source == source and item.target == target), None)

