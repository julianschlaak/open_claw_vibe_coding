# OpenClaw <-> Codex Bridge

This bridge serializes execution and git writes through a single worker.

## Directories
- `ops/jobs/`: incoming jobs (`*.json`)
- `ops/jobs/processed/`: archived processed jobs
- `ops/status/`: status files per job (`<job_id>.json`)
- `ops/logs/`: execution logs (`<job_id>.log`)

## Job Format
See `ops/job_schema.json`.

Minimal example:
```json
{
  "job_id": "job_20260302_001",
  "type": "run_analysis",
  "params": {
    "domain": "catchment_custom",
    "start_year": 1991,
    "end_year": 2020
  },
  "created_at": "2026-03-02T16:50:00Z"
}
```

## Commands
- Healthcheck:
  - `bash ops/bin/healthcheck.sh`
- Submit a job:
  - `bash ops/bin/submit_job.sh /abs/path/to/job.json`
- Process one queued job:
  - `bash ops/bin/worker_once.sh`
- Process all queued jobs:
  - `bash ops/bin/process_queue.sh`

## Supported Job Types
- `healthcheck`
- `run_mhm`:
  - params: `domain` (`test_domain` or `catchment_custom`)
- `run_analysis`:
  - params: `domain`, optional `start_year`, optional `end_year`
- `commit_push`:
  - params: `add_paths` (array), `message` (string), optional `remote`, optional `branch`

## Concurrency Model
- Worker uses a host lock (`/tmp/openclaw_bridge.lock`) via `flock`.
- Only one job executes at a time.
- Git writes are serialized through this same worker.

## Retry Strategy
- Worker retries a failed job up to 3 attempts with exponential backoff (1s, 2s, 4s).
