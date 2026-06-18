FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    WORKDIR=/tmp/morphix \
    CONVERSION_TIMEOUT_SECONDS=900

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    ffmpeg \
    fonts-dejavu \
    imagemagick \
    libreoffice \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/morphix-worker

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "morphix_worker"]

