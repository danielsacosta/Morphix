from __future__ import annotations

from pathlib import Path

from morphix_worker.converters import ConverterRegistry, FFmpegConverter, ImageMagickConverter, SUPPORTED_PAIRS


def test_registry_covers_all_mvp_pairs() -> None:
    registry = ConverterRegistry()
    assert registry.supported_pairs == SUPPORTED_PAIRS
    assert len(registry.supported_pairs) == 15


def test_imagemagick_converter_uses_local_binary(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "image.png"
    source.write_bytes(b"fake")
    calls: list[list[str]] = []

    monkeypatch.setattr("morphix_worker.converters.shutil.which", lambda name: "/usr/bin/magick" if name == "magick" else None)

    def fake_run(command: list[str], timeout_seconds: int) -> None:
        calls.append(command)
        Path(command[-1]).write_bytes(b"converted")

    monkeypatch.setattr("morphix_worker.converters.run_command", fake_run)
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

    monkeypatch.setattr("morphix_worker.converters.run_command", fake_run)
    output = FFmpegConverter().convert(source, tmp_path, "mp3", 30)

    assert output.name == "video.mp3"
    assert calls == [["ffmpeg", "-y", "-i", str(source), str(output)]]

