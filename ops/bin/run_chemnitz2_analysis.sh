#!/bin/bash
# Chemnitz2 Comprehensive Analysis Runner
# Führt die wissenschaftliche Auswertung der mHM-Outputs durch

set -e

echo "=============================================="
echo "Chemnitz2 Comprehensive Analysis"
echo "=============================================="

# Python-Pfad setzen
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"

# Script-Verzeichnis
SCRIPT_DIR="/data/.openclaw/workspace/open_claw_vibe_coding/analysis/scripts"
OUTPUT_DIR="/data/.openclaw/workspace/open_claw_vibe_coding/analysis/plots/chemnitz2"

# Output-Verzeichnis erstellen
mkdir -p "$OUTPUT_DIR"

echo ""
echo "📂 Script: $SCRIPT_DIR/chemnitz2_comprehensive_analysis.py"
echo "📁 Output: $OUTPUT_DIR"
echo ""

# Analyse ausführen
echo "🚀 Starte Analyse..."
python3 "$SCRIPT_DIR/chemnitz2_comprehensive_analysis.py"

echo ""
echo "✅ Analyse abgeschlossen!"
echo ""
echo "📊 Erstellt Plots in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"
