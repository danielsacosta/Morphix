from __future__ import annotations

from pathlib import Path
import zipfile

from morphix_worker.converters.ffmpeg.media_converter import FFmpegConverter
from morphix_worker.converters.imagemagick.image_converter import ImageMagickConverter
from morphix_worker.converters.libreoffice.document_converter import LibreOfficeConverter
from morphix_worker.converters.office.pptx_to_txt import PptxToTxtConverter
from morphix_worker.converters.pdf.pdf_converter import PdfConverter
from morphix_worker.converters.registry import LocalConverterRegistry
from morphix_worker.domain.policies.supported_conversion_policy import SUPPORTED_PAIRS


def test_registry_covers_all_mvp_pairs() -> None:
    registry = LocalConverterRegistry()
    assert registry.supported_pairs == SUPPORTED_PAIRS
    assert len(registry.supported_pairs) == 52


def test_libreoffice_converter_selects_the_requested_filter(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "document.docx"
    source.write_bytes(b"fake")
    calls: list[list[str]] = []

    def fake_run(command: list[str], timeout_seconds: int) -> None:
        del timeout_seconds
        calls.append(command)
        output_format = command[command.index("--convert-to") + 1].split(":", 1)[0]
        output = tmp_path / f"document.{output_format}"
        output.write_bytes(b"converted")

    monkeypatch.setattr("morphix_worker.converters.libreoffice.document_converter.run_command", fake_run)
    output = LibreOfficeConverter().convert(source, tmp_path, "odt", 30)

    assert output.name == "document.odt"
    assert calls[0][calls[0].index("--convert-to") + 1] == "odt"


def test_pdf_converter_exports_all_text_and_first_page_image(tmp_path: Path) -> None:
    import fitz

    source = tmp_path / "document.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Morphix conversion")
    document.save(str(source))
    document.close()

    converter = PdfConverter()
    text_output = converter.convert(source, tmp_path, "txt", 30)
    html_output = converter.convert(source, tmp_path, "html", 30)
    image_output = converter.convert(source, tmp_path, "png", 30)

    assert "Morphix conversion" in text_output.read_text(encoding="utf-8")
    assert "Morphix conversion" in html_output.read_text(encoding="utf-8")
    assert image_output.name == "document.png"
    assert image_output.stat().st_size > 0


def test_pptx_to_txt_extracts_text_from_all_slides(tmp_path: Path) -> None:
    source = tmp_path / "presentation.pptx"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", '<p:sld xmlns:p="p" xmlns:a="a"><a:t>FIRST</a:t></p:sld>')
        archive.writestr("ppt/slides/slide2.xml", '<p:sld xmlns:p="p" xmlns:a="a"><a:t>SECOND</a:t></p:sld>')

    output = PptxToTxtConverter().convert(source, tmp_path, "txt", 30)

    assert output.read_text(encoding="utf-8") == "FIRST\n\nSECOND\n"


def test_imagemagick_converter_uses_local_binary(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "image.png"
    source.write_bytes(b"fake")
    calls: list[list[str]] = []

    monkeypatch.setattr("morphix_worker.converters.imagemagick.image_converter.shutil.which", lambda name: "/usr/bin/magick" if name == "magick" else None)

    def fake_run(command: list[str], timeout_seconds: int) -> None:
        calls.append(command)
        Path(command[-1]).write_bytes(b"converted")

    monkeypatch.setattr("morphix_worker.converters.imagemagick.image_converter.run_command", fake_run)
    output = ImageMagickConverter().convert(source, tmp_path, "webp", 30)

    assert output.name == "image.webp"
    assert calls == [["/usr/bin/magick", str(source), str(output)]]


def test_ffmpeg_converter_uses_ffmpeg(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "video.mp4"
    source.write_bytes(b"fake")
    calls: list[list[str]] = []

    def fake_run(command: list[str], timeout_seconds: int) -> None:
        calls.append(command)
        Path(command[-1]).write_bytes(b"converted")

    monkeypatch.setattr("morphix_worker.converters.ffmpeg.media_converter.run_command", fake_run)
    output = FFmpegConverter().convert(source, tmp_path, "mp3", 30)

    assert output.name == "video.mp3"
    assert calls == [["ffmpeg", "-y", "-i", str(source), str(output)]]
