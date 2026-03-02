#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-1lxa-openclaw-1}"
WORKDIR="${OPENCLAW_WORKDIR:-/data/.openclaw/workspace/open_claw_vibe_coding}"
PY="/data/.openclaw/workspace/miniforge/bin/python"
SSH_KEY="/data/.openclaw/workspace/.ssh/id_ed25519"

ok() { printf "[OK] %s\n" "$1"; }
fail() { printf "[FAIL] %s\n" "$1"; exit 1; }

command -v docker >/dev/null || fail "docker not available on host"
ok "docker available"

docker inspect "$CONTAINER" >/dev/null 2>&1 || fail "container not found: $CONTAINER"
ok "container present"

docker exec "$CONTAINER" test -d "$WORKDIR/.git" || fail "repo not found in container: $WORKDIR"
ok "repo present in container"

docker exec "$CONTAINER" test -x "$PY" || fail "miniforge python missing in container: $PY"
ok "miniforge python present"

docker exec "$CONTAINER" "$PY" - <<'PY' >/dev/null || fail "python imports failed in container"
import numpy, pandas, scipy, matplotlib
print("ok")
PY
ok "core python libs import"

docker exec "$CONTAINER" test -f "$SSH_KEY" || fail "ssh key missing in container: $SSH_KEY"
ok "ssh key present"

docker exec "$CONTAINER" bash -lc "command -v /usr/local/bin/openclaw-git-serial >/dev/null" || fail "openclaw-git-serial missing in container"
ok "openclaw-git-serial available"

ok "healthcheck complete"
