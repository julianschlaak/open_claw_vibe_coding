#!/bin/bash
# mHM Environment Activation Script
# Auto-generated: 2026-03-02

# Activate conda environment
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
eval "$(conda shell.bash hook)"

# Display mHM info
echo "=================================="
echo "mHM Environment Activated"
echo "=================================="
mhm --version
echo ""
echo "Usage: mhm [options] [path_to_config]"
echo ""
echo "Quick test: mhm ./test_domain"
echo "=================================="
