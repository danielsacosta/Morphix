# Morphix Worker

Python worker executed as an ECS Fargate task in AWS or as a Docker Compose process locally. In AWS it uses S3, DynamoDB and SQS; locally it uses the shared filesystem, SQLite and Redis without changing the conversion pipeline.

## Engines

- LibreOffice headless: office and tabular conversions to PDF, TXT, HTML, ODT, ODS and ODP.
- pdf2docx/PyMuPDF: PDF to DOCX, TXT, HTML, PNG and JPG.
- openpyxl: CSV to XLSX and XLSX to CSV.
- ImageMagick: PNG, JPG, SVG, GIF and TIFF image conversions.
- FFmpeg: MP4, MOV, AVI, MKV, M4V, FLV and 3GP video conversions plus WAV, MP3, AAC, FLAC, OGG, M4A, OPUS and AIFF audio conversions.

The worker does not call external conversion APIs.

## Real conversion matrix

From the repository root, run `./scripts/run-conversion-e2e.sh` to build the worker image, generate valid temporary fixtures and execute all 52 conversion routes with the real LibreOffice, PyMuPDF, ImageMagick/rsvg and FFmpeg binaries. The runner validates structure, preserved text, media duration and image SSIM/PSNR, then removes the entire temporary workspace on success, failure or interruption.
