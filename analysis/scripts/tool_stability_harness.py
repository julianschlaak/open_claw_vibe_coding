#!/usr/bin/env python3
"""Stability harness for OpenClaw tool usage via chat.send/agent.wait."""

from __future__ import annotations

import json
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

CONTAINER = "openclaw-1lxa-openclaw-1"
SESSION_KEY = "agent:main:main"
REPEATS = 10


@dataclass
class AttemptResult:
    tool: str
    attempt: int
    ok: bool
    reason: str
    run_id: str
    expected_token: str


def run_gateway(method: str, params: Dict, timeout_ms: int = 120000) -> Dict:
    payload = json.dumps(params, ensure_ascii=False)
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "sh",
        "-lc",
        f"openclaw gateway call {method} --json --params {json.dumps(payload)}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=max(1, timeout_ms // 1000))
    if proc.returncode != 0:
        raise RuntimeError(f"{method} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(proc.stdout)


def get_history() -> Dict:
    return run_gateway("chat.history", {"sessionKey": SESSION_KEY}, timeout_ms=30000)


def flatten_text(msg: Dict) -> str:
    parts = msg.get("content") or []
    texts: List[str] = []
    for p in parts:
        if isinstance(p, dict) and isinstance(p.get("text"), str):
            texts.append(p["text"])
    return "\n".join(texts)


def evaluate_attempt(tool: str, start_ts: int, expected_token: str) -> tuple[bool, str]:
    history = get_history()
    recent = [m for m in history.get("messages", []) if int(m.get("timestamp", 0)) >= start_ts]
    tool_results = [m for m in recent if m.get("role") == "toolResult"]
    assistant_msgs = [m for m in recent if m.get("role") == "assistant"]

    for tr in tool_results:
        text = flatten_text(tr)
        if tr.get("isError"):
            if "Tool  not found" in text or "tool not found" in text.lower():
                return False, "tool_not_found"
            return False, "tool_error"

    combined_assistant = "\n".join(flatten_text(m) for m in assistant_msgs)
    if expected_token in combined_assistant:
        return True, "ok"

    return False, "missing_expected_token"


def prompt_for(tool: str, token: str) -> str:
    uid = token.lower()
    if tool == "write":
        return (
            f"TOOLTEST {tool}: Nutze genau das Tool write, um die Datei "
            f"/tmp/{uid}.txt mit Inhalt '{token}' zu schreiben. "
            f"Antworte danach exakt mit {token}."
        )
    if tool == "exec":
        return (
            f"TOOLTEST {tool}: Nutze genau das Tool exec und führe 'echo {token}' aus. "
            f"Antworte danach exakt mit {token}."
        )
    if tool == "sessions_spawn":
        return (
            f"TOOLTEST {tool}: Nutze genau das Tool sessions_spawn, starte einen Sub-Agenten mit "
            f"Task 'Antworte nur {token}'. Antworte danach exakt mit {token}."
        )
    raise ValueError(tool)


def run_attempt(tool: str, attempt: int) -> AttemptResult:
    expected = f"TOOLTEST_{tool.upper()}_{attempt}_{uuid.uuid4().hex[:6]}"
    run_id = f"codex-{tool}-{attempt}-{uuid.uuid4().hex[:8]}"
    message = prompt_for(tool, expected)
    start_ts = int(time.time() * 1000)

    run_gateway(
        "chat.send",
        {
            "sessionKey": SESSION_KEY,
            "message": message,
            "idempotencyKey": run_id,
        },
        timeout_ms=30000,
    )

    run_gateway("agent.wait", {"runId": run_id}, timeout_ms=180000)
    ok, reason = evaluate_attempt(tool, start_ts, expected)
    return AttemptResult(tool=tool, attempt=attempt, ok=ok, reason=reason, run_id=run_id, expected_token=expected)


def main() -> None:
    results: List[AttemptResult] = []
    tools = ["write", "exec", "sessions_spawn"]

    for tool in tools:
        for i in range(1, REPEATS + 1):
            try:
                res = run_attempt(tool, i)
            except Exception as exc:
                res = AttemptResult(tool=tool, attempt=i, ok=False, reason=f"exception:{type(exc).__name__}", run_id="", expected_token="")
            results.append(res)
            time.sleep(0.5)

    summary: Dict[str, Dict] = {}
    for tool in tools:
        subset = [r for r in results if r.tool == tool]
        ok_count = sum(1 for r in subset if r.ok)
        summary[tool] = {
            "attempts": len(subset),
            "successes": ok_count,
            "failures": len(subset) - ok_count,
            "success_rate": round((ok_count / len(subset)) * 100.0, 2) if subset else 0.0,
            "reasons": {},
        }
        for r in subset:
            summary[tool]["reasons"][r.reason] = summary[tool]["reasons"].get(r.reason, 0) + 1

    out = {
        "timestamp": int(time.time()),
        "session_key": SESSION_KEY,
        "repeats_per_tool": REPEATS,
        "summary": summary,
        "attempt_details": [r.__dict__ for r in results],
    }

    repo = Path(__file__).resolve().parents[2]
    out_file = repo / "analysis" / "results" / "tool_stability_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
