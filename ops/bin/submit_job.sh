#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JOB_SRC="${1:-}"

[[ -n "$JOB_SRC" ]] || { echo "usage: submit_job.sh <job.json>"; exit 2; }
[[ -f "$JOB_SRC" ]] || { echo "job file not found: $JOB_SRC"; exit 2; }

python3 - <<PY "$JOB_SRC" "$REPO_ROOT/ops/jobs"
import json, pathlib, sys
src = pathlib.Path(sys.argv[1])
outdir = pathlib.Path(sys.argv[2])
obj = json.loads(src.read_text())
for k in ("job_id", "type", "params", "created_at"):
    if k not in obj:
        raise SystemExit(f"missing required key: {k}")
job_id = str(obj["job_id"]).strip()
if not job_id:
    raise SystemExit("job_id is empty")
out = outdir / f"{job_id}.json"
out.write_text(json.dumps(obj, indent=2) + "\n")
print(out)
PY
