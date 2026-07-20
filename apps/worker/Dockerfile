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
    librsvg2-bin \
    libreoffice \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/morphix-worker

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv
COPY pyproject.toml README.md ./
COPY src ./src

RUN uv pip install --system --no-cache .

ENTRYPOINT ["python", "-m", "morphix_worker"]
