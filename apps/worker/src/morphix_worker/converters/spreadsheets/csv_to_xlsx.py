from __future__ import annotations

import csv
from pathlib import Path

from ..common import expected_output


class CsvToXlsxConverter:
    def convert(self, input_path: Path, output_dir: Path, target_format: str, timeout_seconds: int) -> Path:
        if target_format != "xlsx":
            raise ValueError("CSV converter only supports XLSX output")

        from openpyxl import Workbook

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Sheet1"
        with input_path.open(newline="", encoding="utf-8-sig") as source_file:
            reader = csv.reader(source_file)
            for row in reader:
                worksheet.append(row)

        output_path = expected_output(input_path, output_dir, target_format)
        workbook.save(output_path)
        return output_path

