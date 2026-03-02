#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JOBS_DIR="$REPO_ROOT/ops/jobs"
PROCESSED_DIR="$JOBS_DIR/processed"
STATUS_DIR="$REPO_ROOT/ops/status"
LOGS_DIR="$REPO_ROOT/ops/logs"
LOCK_FILE="/tmp/openclaw_bridge.lock"

mkdir -p "$PROCESSED_DIR" "$STATUS_DIR" "$LOGS_DIR"

exec 9>"$LOCK_FILE"
flock -n 9 || { echo "worker locked, another instance is running"; exit 3; }

job_file="$(find "$JOBS_DIR" -maxdepth 1 -type f -name "*.json" | sort | head -n 1 || true)"
if [[ -z "$job_file" ]]; then
  echo "no queued jobs"
  exit 0
fi

job_id="$(python3 - <<PY "$job_file"
import json, sys
obj = json.load(open(sys.argv[1]))
print(obj["job_id"])
PY
)"
job_type="$(python3 - <<PY "$job_file"
import json, sys
obj = json.load(open(sys.argv[1]))
print(obj["type"])
PY
)"

status_file="$STATUS_DIR/${job_id}.json"
log_file="$LOGS_DIR/${job_id}.log"

write_status() {
  local status="$1"
  local message="$2"
  python3 - <<PY "$status_file" "$job_id" "$job_type" "$status" "$message"
import json, pathlib, sys, datetime
p = pathlib.Path(sys.argv[1])
obj = {
  "job_id": sys.argv[2],
  "type": sys.argv[3],
  "status": sys.argv[4],
  "message": sys.argv[5],
  "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
}
p.write_text(json.dumps(obj, indent=2) + "\n")
PY
}

run_job() {
  case "$job_type" in
    healthcheck)
      bash "$REPO_ROOT/ops/bin/healthcheck.sh"
      ;;
    run_mhm)
      local domain
      domain="$(python3 - <<PY "$job_file"
import json, sys
obj = json.load(open(sys.argv[1]))
print(obj["params"].get("domain", ""))
PY
)"
      bash "$REPO_ROOT/ops/bin/run_mhm.sh" "$domain"
      ;;
    run_analysis)
      local domain start_year end_year
      read -r domain start_year end_year < <(python3 - <<PY "$job_file"
import json, sys
obj = json.load(open(sys.argv[1]))
p = obj["params"]
print(p.get("domain", ""), p.get("start_year", ""), p.get("end_year", ""))
PY
)
      bash "$REPO_ROOT/ops/bin/run_analysis.sh" "$domain" "$start_year" "$end_year"
      ;;
    verify)
      local domain
      domain="$(python3 - <<PY "$job_file"
import json, sys
obj = json.load(open(sys.argv[1]))
print(obj["params"].get("domain", "catchment_custom"))
PY
)"
      bash "$REPO_ROOT/ops/bin/run_verify.sh" "$domain"
      ;;
    commit_push)
      python3 - <<PY "$job_file" "$REPO_ROOT/ops/.commit_args"
import json, sys, pathlib
obj = json.load(open(sys.argv[1]))
p = obj["params"]
remote = p.get("remote", "origin")
branch = p.get("branch", "main")
message = p.get("message", "[AUTO] Bridge commit")
paths = p.get("add_paths", [])
if not paths:
    raise SystemExit("commit_push requires params.add_paths")
out = pathlib.Path(sys.argv[2])
out.write_text("\n".join([remote, branch, message, *paths]) + "\n")
PY
      mapfile -t args < "$REPO_ROOT/ops/.commit_args"
      bash "$REPO_ROOT/ops/bin/commit_push.sh" "${args[@]}"
      ;;
    *)
      echo "unsupported job type: $job_type"
      return 2
      ;;
  esac
}

write_status "running" "started"

attempt=1
max_attempts=3
while :; do
  if run_job >>"$log_file" 2>&1; then
    write_status "success" "completed"
    mv "$job_file" "$PROCESSED_DIR/$(basename "$job_file")"
    echo "job $job_id success"
    exit 0
  fi

  if [[ "$attempt" -ge "$max_attempts" ]]; then
    write_status "failed" "failed after ${max_attempts} attempts"
    mv "$job_file" "$PROCESSED_DIR/$(basename "$job_file")"
    echo "job $job_id failed"
    exit 1
  fi

  sleep_time=$((2 ** (attempt - 1)))
  echo "job $job_id attempt $attempt failed, retrying in ${sleep_time}s" >>"$log_file"
  sleep "$sleep_time"
  attempt=$((attempt + 1))
done
