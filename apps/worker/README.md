# Morphix Worker

Python worker executed as an ECS Fargate task. It downloads an input file from S3, converts it locally, uploads the output to S3, and updates the DynamoDB job record.

## Engines

- LibreOffice headless: DOCX/XLSX/PPTX to PDF.
- pdf2docx/PyMuPDF: PDF to DOCX.
- openpyxl: CSV to XLSX and XLSX to CSV.
- ImageMagick: PNG/JPG/WebP image conversions.
- FFmpeg: audio and video conversions.

The worker does not call external conversion APIs.

