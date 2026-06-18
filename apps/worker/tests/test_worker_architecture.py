from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "morphix_worker"


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def python_files(path: Path) -> list[Path]:
    return [file for file in path.rglob("*.py") if "__pycache__" not in file.parts]


def test_domain_has_no_aws_or_tool_imports() -> None:
    banned = {"boto3", "botocore", "subprocess", "fitz", "pdf2docx", "openpyxl"}
    offenders = {file: imported_roots(file) & banned for file in python_files(ROOT / "domain")}
    offenders = {file: imports for file, imports in offenders.items() if imports}
    assert offenders == {}


def test_pipeline_has_no_aws_imports() -> None:
    banned = {"boto3", "botocore"}
    offenders = {file: imported_roots(file) & banned for file in python_files(ROOT / "application")}
    offenders = {file: imports for file, imports in offenders.items() if imports}
    assert offenders == {}

