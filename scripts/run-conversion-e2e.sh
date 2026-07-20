#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
temporary_dir="$(mktemp -d -t morphix-conversions.XXXXXX)"

cleanup() {
  rm -rf -- "$temporary_dir"
}
trap cleanup EXIT INT TERM

docker compose -f "$repo_root/docker-compose.yml" run --rm --no-deps \
  -v "$repo_root/scripts/conversion_e2e_matrix.py:/tmp/conversion_e2e_matrix.py:ro" \
  -v "$temporary_dir:/tmp/morphix-e2e:rw" \
  worker python /tmp/conversion_e2e_matrix.py --workspace /tmp/morphix-e2e
