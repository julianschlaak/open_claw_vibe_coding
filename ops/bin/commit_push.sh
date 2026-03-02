#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-1lxa-openclaw-1}"
WORKDIR="${OPENCLAW_WORKDIR:-/data/.openclaw/workspace/open_claw_vibe_coding}"
REMOTE="${1:-origin}"
BRANCH="${2:-main}"
MESSAGE="${3:-[AUTO] Bridge commit}"
shift 3 || true

if [[ "$#" -eq 0 ]]; then
  echo "usage: commit_push.sh <remote> <branch> <message> <path1> [path2 ...]"
  exit 2
fi

docker exec "$CONTAINER" bash -lc '
  set -euo pipefail
  WORKDIR="$1"; REMOTE="$2"; BRANCH="$3"; MESSAGE="$4"; shift 4
  cd "$WORKDIR"
  /usr/local/bin/openclaw-git-serial add "$@"
  /usr/local/bin/openclaw-git-serial commit -m "$MESSAGE" || true
  /usr/local/bin/openclaw-git-serial push "$REMOTE" "$BRANCH"
' _ "$WORKDIR" "$REMOTE" "$BRANCH" "$MESSAGE" "$@"
