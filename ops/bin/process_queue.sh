#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

while true; do
  if ! bash "$REPO_ROOT/ops/bin/worker_once.sh"; then
    true
  fi
  pending="$(find "$REPO_ROOT/ops/jobs" -maxdepth 1 -type f -name "*.json" | wc -l | tr -d " ")"
  [[ "$pending" -eq 0 ]] && break
done
