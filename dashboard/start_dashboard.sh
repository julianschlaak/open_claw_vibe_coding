#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
echo "Starting Drought Dashboard v3.0..."

pkill -f "streamlit run app.py" 2>/dev/null || true
sleep 2

export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
python3 -m streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.serverAddress localhost \
  --server.maxUploadSize 50
