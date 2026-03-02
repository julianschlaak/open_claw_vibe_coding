#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-1lxa-openclaw-1}"
WORKDIR="${OPENCLAW_WORKDIR:-/data/.openclaw/workspace/open_claw_vibe_coding}"
DOMAIN="${1:-}"
START_YEAR="${2:-}"
END_YEAR="${3:-}"

[[ -n "$DOMAIN" ]] || { echo "usage: run_analysis.sh <domain> [start_year] [end_year]"; exit 2; }

docker exec \
  -e OC_WORKDIR="$WORKDIR" \
  -e OC_DOMAIN="$DOMAIN" \
  -e OC_START_YEAR="$START_YEAR" \
  -e OC_END_YEAR="$END_YEAR" \
  "$CONTAINER" bash -lc '
    set -euo pipefail
    cd "$OC_WORKDIR/analysis/scripts"
    PY="/data/.openclaw/workspace/miniforge/bin/python"
    args=(--domain "$OC_DOMAIN")
    if [[ -n "${OC_START_YEAR:-}" ]]; then args+=(--start-year "$OC_START_YEAR"); fi
    if [[ -n "${OC_END_YEAR:-}" ]]; then args+=(--end-year "$OC_END_YEAR"); fi
    "$PY" drought_pipeline.py "${args[@]}"
    "$PY" drought_analysis_advanced.py "${args[@]}"
  '
