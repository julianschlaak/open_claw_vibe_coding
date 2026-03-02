#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-1lxa-openclaw-1}"
WORKDIR="${OPENCLAW_WORKDIR:-/data/.openclaw/workspace/open_claw_vibe_coding}"
DOMAIN="${1:-}"

[[ -n "$DOMAIN" ]] || { echo "usage: run_mhm.sh <test_domain|catchment_custom>"; exit 2; }
[[ "$DOMAIN" == "test_domain" || "$DOMAIN" == "catchment_custom" ]] || { echo "invalid domain: $DOMAIN"; exit 2; }

docker exec "$CONTAINER" bash -lc "set -euo pipefail; export PATH=\"/data/.openclaw/workspace/miniforge/bin:\$PATH\"; cd \"$WORKDIR/code/mhm\"; mhm \"./$DOMAIN\""
