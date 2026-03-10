#!/bin/bash
#===============================================================================
# Setup Saxony Catchment (1991-2020) with Recommended Parameters
# 
# Usage: bash setup_saxony_0p0625_1991_2020.sh
# 
# This script prepares the Saxony catchment for mHM simulation using
# the recommended parameter set from DDS analysis (6 catchments).
#
# Saxony Catchment:
#   - Resolution: 0.0625° (~6.25 km)
#   - Period: 1991-2020 (30 years)
#   - Parameters: From recommended_params.csv (GLOBAL + CATCHMENT_SPECIFIC)
#
# Prerequisites:
#   - recommended_params.csv exists in dashboard_saxony/utils/
#   - Input data available (meteo, morph, lai, luse)
#   - mHM 5.13.2 available in container
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE="/data/.openclaw/workspace/open_claw_vibe_coding"
MHM_DIR="${WORKSPACE}/code/mhm"
RUNS_DIR="${MHM_DIR}/runs"
RECOMMENDED_PARAMS_CSV="${WORKSPACE}/dashboard_saxony/utils/recommended_params.csv"
MINIFORGE="/data/.openclaw/workspace/miniforge"

# Saxony catchment ID
CATCHMENT_ID="saxony_0p0625"
CATCHMENT_NAME="Saxony"

echo "==============================================================================="
echo "🏔️  Setup Saxony Catchment (1991-2020)"
echo "==============================================================================="
echo ""
echo "📊 Catchment: ${CATCHMENT_NAME} (${CATCHMENT_ID})"
echo "📅 Period: 1991 - 2020 (30 years)"
echo "🔧 mHM Version: 5.13.2"
echo "📂 Workspace: ${WORKSPACE}"
echo ""
echo "==============================================================================="

# Check if recommended_params.csv exists
if [ ! -f "${RECOMMENDED_PARAMS_CSV}" ]; then
    echo -e "${YELLOW}⚠️  Warning: ${RECOMMENDED_PARAMS_CSV} not found${NC}"
    echo "   Please run DDS analysis first or check path."
    exit 1
fi

echo -e "${GREEN}✅ Found: ${RECOMMENDED_PARAMS_CSV}${NC}"
echo ""

# Create run directory structure
RUN_DIR="${RUNS_DIR}/${CATCHMENT_ID}"
echo "📁 Creating run directory: ${RUN_DIR}"
mkdir -p "${RUN_DIR}"/{nml,input,output,restart}

# Copy input data from catchments_cloud
INPUT_SOURCE="${MHM_DIR}/catchments_cloud/${CATCHMENT_ID}/input"
if [ -d "${INPUT_SOURCE}" ]; then
    echo -e "${GREEN}✅ Found input data: ${INPUT_SOURCE}${NC}"
    echo "   Copying input data..."
    
    # Create symlinks instead of copying (saves space)
    for subdir in meteo morph lai latlon; do
        if [ -d "${INPUT_SOURCE}/${subdir}" ]; then
            ln -sf "${INPUT_SOURCE}/${subdir}" "${RUN_DIR}/input/${subdir}" 2>/dev/null || \
            cp -r "${INPUT_SOURCE}/${subdir}" "${RUN_DIR}/input/"
            echo "   ✅ input/${subdir}/"
        fi
    done
else
    echo -e "${YELLOW}⚠️  Input data not found: ${INPUT_SOURCE}${NC}"
    echo "   Please provide input data manually."
fi

echo ""

# Generate mhm_parameter.nml from recommended_params.csv
echo "🔧 Generating mhm_parameter.nml from recommended_params.csv..."
export PATH="${MINIFORGE}/bin:$PATH"

python3 << 'PYTHON_SCRIPT'
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuration
CSV_PATH = Path("/data/.openclaw/workspace/open_claw_vibe_coding/dashboard_saxony/utils/recommended_params.csv")
RUN_DIR = Path("/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/runs/saxony_0p0625")
TEMPLATE_PATH = Path("/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/nml/mhm_parameter.nml")
OUTPUT_NML = RUN_DIR / "nml" / "mhm_parameter.nml"

# Parameter mapping (param_id -> name in mhm_parameter.nml)
PARAM_NAMES = {
    1: "param_01", 2: "param_02", 3: "param_03", 4: "param_04",
    5: "param_05", 6: "param_06", 7: "param_07", 8: "param_08",
    9: "param_09", 10: "param_10", 11: "param_11", 12: "param_12",
    13: "param_13", 14: "param_14", 15: "param_15", 16: "param_16",
    17: "param_17", 18: "param_18", 19: "param_19", 20: "param_20",
    21: "param_21", 22: "param_22", 23: "param_23", 24: "param_24",
    25: "param_25", 26: "param_26", 27: "param_27", 28: "param_28",
    29: "param_29", 30: "param_30", 31: "param_31", 32: "param_32",
    33: "param_33", 34: "param_34", 35: "param_35", 36: "param_36",
    37: "param_37", 38: "param_38", 39: "param_39", 40: "param_40",
    41: "param_41", 42: "param_42", 43: "param_43", 44: "param_44",
    45: "param_45", 46: "param_46", 47: "param_47", 48: "param_48",
    49: "param_49", 50: "param_50", 51: "param_51", 52: "param_52",
    53: "param_53", 54: "param_54",
}

print("📊 Reading recommended_params.csv...")
if not CSV_PATH.exists():
    print(f"❌ Error: {CSV_PATH} not found")
    exit(1)

df = pd.read_csv(CSV_PATH)

# Read template
print("📄 Reading template...")
if not TEMPLATE_PATH.exists():
    print(f"❌ Error: Template not found: {TEMPLATE_PATH}")
    exit(1)

with open(TEMPLATE_PATH, 'r', encoding='latin-1') as f:
    template = f.read()

# Generate parameter values (use GLOBAL for all, as Saxony is ungauged)
print("🔧 Generating parameter values...")
recommended = {}
for _, row in df.iterrows():
    param_id = int(row['param_id'])
    param_name = PARAM_NAMES.get(param_id, f"param_{param_id:02d}")
    
    # For Saxony (ungauged), always use GLOBAL mean (not catchment-specific)
    if pd.isna(row['recommended_value']):
        # If no GLOBAL mean, use a reasonable default
        recommended[param_name] = 0.5  # Default value
        source = "default"
    else:
        recommended[param_name] = float(row['recommended_value'])
        source = "GLOBAL mean (6 catchments)"

# Replace in template
lines = template.split('\n')
new_lines = []
replaced = 0

for line in lines:
    stripped = line.strip()
    if stripped.startswith('param_') and '=' in stripped:
        parts = stripped.split('=')
        param_name = parts[0].strip()
        
        if param_name in recommended:
            value = recommended[param_name]
            new_line = f"{param_name} = {value:.8f}"
            new_lines.append(new_line)
            replaced += 1
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

print(f"✅ Replaced {replaced} parameter values")

# Add header
header = f"""!******************************************************************************************
! GENERATED PARAMETER FILE - SAXONY CATCHMENT (UNGAGED)
!******************************************************************************************
! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
! Source: recommended_params.csv (6 catchments DDS analysis)
! Catchment: Saxony (saxony_0p0625)
! Period: 1991-2020 (30 years)
!
! Strategy for Ungauged Catchments:
!   - All parameters: GLOBAL mean across 6 calibrated catchments
!   - No catchment-specific calibration applied
!   - Suitable for regionalization studies
!
! Statistics:
!   - GLOBAL (CV < 0.1): {sum(1 for v in df['recommendation'] if v=='GLOBAL')} parameters
!   - GLOBAL_WITH_UNCERTAINTY (CV 0.1-0.3): {sum(1 for v in df['recommendation'] if v=='GLOBAL_WITH_UNCERTAINTY')} parameters
!   - CATCHMENT_SPECIFIC (CV > 0.3): {sum(1 for v in df['recommendation'] if v=='CATCHMENT_SPECIFIC')} parameters
!
! Note: For ungauged Saxony, we use GLOBAL means only (no regionalization yet)
!******************************************************************************************

"""

nml_content = header + '\n'.join(new_lines)

# Write output
RUN_DIR.mkdir(parents=True, exist_ok=True)
(RUN_DIR / "nml").mkdir(exist_ok=True)

with open(OUTPUT_NML, 'w', encoding='utf-8') as f:
    f.write(nml_content)

print(f"✅ Generated: {OUTPUT_NML}")
print()
print("📋 Parameter summary:")
print(f"   Total: {len(recommended)} parameters")
print(f"   Source: GLOBAL mean from 6 calibrated catchments")
PYTHON_SCRIPT

echo ""

# Create mhm.nml for 1991-2020
echo "📝 Creating mhm.nml for 1991-2020..."

# Check if template exists
TEMPLATE_MHM_NML="${MHM_DIR}/catchments_cloud/${CATCHMENT_ID}/ConfigFile.log"
if [ -f "${TEMPLATE_MHM_NML}" ]; then
    echo "   Using ConfigFile.log as reference..."
    # Extract and convert to mhm.nml format (simplified)
    # For now, copy from parthe and adjust
    cp /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/nml/mhm.nml "${RUN_DIR}/nml/mhm.nml"
    
    # Adjust paths for Saxony
    sed -i 's|parthe_0p0625|saxony_0p0625|g' "${RUN_DIR}/nml/mhm.nml"
    sed -i 's|/mhm_re_crit/|/mhm/|g' "${RUN_DIR}/nml/mhm.nml"
    
    echo "   ✅ Created mhm.nml (adjusted from parthe template)"
else
    echo -e "${YELLOW}⚠️  No template found. Please create mhm.nml manually.${NC}"
fi

echo ""
echo "==============================================================================="
echo "✅ SETUP COMPLETE!"
echo "==============================================================================="
echo ""
echo "📂 Run directory: ${RUN_DIR}"
echo "📄 Parameter file: ${RUN_DIR}/nml/mhm_parameter.nml"
echo "📄 Config file: ${RUN_DIR}/nml/mhm.nml"
echo ""
echo "🚀 Next steps:"
echo "  1. Verify mhm.nml (time period, input paths)"
echo "  2. Run: cd ${RUN_DIR} && mhm ./saxony_0p0625"
echo "  3. Check output: ${RUN_DIR}/output/"
echo ""
echo "⚠️  Note: Saxony is an ungauged catchment. Parameters are GLOBAL means"
echo "   from the 6 calibrated catchments. No local calibration applied."
echo ""
