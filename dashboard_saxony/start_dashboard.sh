#!/usr/bin/env bash
set -euo pipefail

cd /docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding/dashboard_saxony
export PATH="/docker/openclaw-1lxa/data/.openclaw/workspace/miniforge/bin:$PATH"

pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8502
