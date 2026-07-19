# Morphix Worker

Python worker executed as an ECS Fargate task in AWS or as a Docker Compose process locally. In AWS it uses S3, DynamoDB and SQS; locally it uses the shared filesystem, SQLite and Redis without changing the conversion pipeline.

## Engines

- LibreOffice headless: DOCX/XLSX/PPTX to PDF.
- pdf2docx/PyMuPDF: PDF to DOCX.
- openpyxl: CSV to XLSX and XLSX to CSV.
- ImageMagick: PNG/JPG/WebP image conversions.
- FFmpeg: audio and video conversions.

The worker does not call external conversion APIs.
