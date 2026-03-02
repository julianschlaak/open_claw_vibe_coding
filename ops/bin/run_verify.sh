#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-1lxa-openclaw-1}"
WORKDIR="${OPENCLAW_WORKDIR:-/data/.openclaw/workspace/open_claw_vibe_coding}"
DOMAIN="${1:-catchment_custom}"

docker exec \
  -e OC_WORKDIR="$WORKDIR" \
  -e OC_DOMAIN="$DOMAIN" \
  "$CONTAINER" bash -lc '
    set -euo pipefail
    cd "$OC_WORKDIR"
    PY="/data/.openclaw/workspace/miniforge/bin/python"

    "$PY" - <<'"'"'PY'"'"'
import json
import os
from pathlib import Path
import pandas as pd

repo = Path(os.environ["OC_WORKDIR"])
domain = os.environ["OC_DOMAIN"]

errors = []
checks = {}

# 1) Volumetric soil moisture plausibility from results (expected in [0,1] range)
monthly = repo / "analysis" / "results" / domain / "monthly_drought_indices.csv"
if not monthly.exists():
    errors.append(f"missing results file: {monthly}")
else:
    df = pd.read_csv(monthly)
    sm = pd.to_numeric(df.get("sm"), errors="coerce")
    checks["sm_min"] = float(sm.min())
    checks["sm_max"] = float(sm.max())
    checks["sm_mean"] = float(sm.mean())
    if sm.isna().all() or float(sm.max()) > 1.5 or float(sm.min()) < -0.1:
        errors.append("sm range implausible (expected ~0..1 m3/m3)")

# 2) Discharge validation data + metrics code presence
daily = repo / "analysis" / "results" / domain / "daily_discharge.csv"
if not daily.exists():
    errors.append(f"missing discharge results: {daily}")
else:
    dfd = pd.read_csv(daily)
    qobs = pd.to_numeric(dfd.get("qobs"), errors="coerce")
    qsim = pd.to_numeric(dfd.get("qsim"), errors="coerce")
    checks["qobs_non_nan"] = int(qobs.notna().sum())
    checks["qsim_non_nan"] = int(qsim.notna().sum())
    if qobs.notna().sum() == 0 or qsim.notna().sum() == 0:
        errors.append("qobs/qsim missing in daily_discharge.csv")

pipe = (repo / "analysis" / "scripts" / "drought_pipeline.py").read_text(errors="ignore")
needles = ["Qobs (Gemessen)", "Qsim (Modell)", "KGE:", "RMSE:", "MAE:", "NSE:", "Bias:"]
checks["discharge_plot_markers_present"] = all(n in pipe for n in needles)
if not checks["discharge_plot_markers_present"]:
    errors.append("discharge plot labels/metrics markers missing in code")

# 3) Flat folder structure check (no nested normal/advanced/legacy folders)
plots_root = repo / "analysis" / "plots"
flat_ok = True
for d in ["test_domain", "catchment_custom"]:
    p = plots_root / d
    if not p.exists():
        errors.append(f"missing plots folder: {p}")
        flat_ok = False
        continue
    nested = [x.name for x in p.iterdir() if x.is_dir()]
    checks[f"{d}_nested_dirs"] = nested
    if nested:
        flat_ok = False
        errors.append(f"{d} has nested plot dirs: {nested}")
checks["flat_structure_ok"] = flat_ok

# 4) Plot completeness: 10 plots per domain
for d in ["test_domain", "catchment_custom"]:
    p = plots_root / d
    count = len(list(p.glob("*.png"))) if p.exists() else 0
    checks[f"{d}_png_count"] = count
    if count != 10:
        errors.append(f"{d} expected 10 png plots, found {count}")

status = "success" if not errors else "failed"
print(json.dumps({"status": status, "checks": checks, "errors": errors}, indent=2))
if errors:
    raise SystemExit(1)
PY
  '
