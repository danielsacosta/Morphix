#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${APP_DIR}/.lambda_build"
DIST_DIR="${APP_DIR}/lambda_dist"
PACKAGE_PATH="${DIST_DIR}/morphix-api.zip"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
LAMBDA_PLATFORM="${LAMBDA_PLATFORM:-x86_64-manylinux2014}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to build the Lambda package." >&2
  exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
  echo "zip is required to build the Lambda package." >&2
  exit 1
fi

rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

(
  cd "${APP_DIR}"
  uv pip install \
    --python "${PYTHON_BIN}" \
    --python-platform "${LAMBDA_PLATFORM}" \
    --target "${BUILD_DIR}" \
    .
)

find "${BUILD_DIR}" \
  -type d -name "__pycache__" \
  -prune -exec rm -rf {} +
find "${BUILD_DIR}" -type f -name "*.pyc" -delete

(
  cd "${BUILD_DIR}"
  zip -qr "${PACKAGE_PATH}" .
)

rm -rf "${BUILD_DIR}"

echo "${PACKAGE_PATH}"
