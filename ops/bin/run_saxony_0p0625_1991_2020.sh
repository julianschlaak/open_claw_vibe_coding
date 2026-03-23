#!/bin/bash
#===============================================================================
# Run Saxony Catchment (1991-2020) Simulation
# 
# Usage: bash run_saxony_0p0625_1991_2020.sh
# 
# This script runs mHM for the Saxony catchment using the
# recommended parameter set from DDS analysis (GLOBAL parameters).
#
# Saxony Catchment:
#   - Resolution: 0.0625° (~6.25 km)
#   - Period: 1991-2020 (30 years)
#   - Parameters: From recommended_params.csv (GLOBAL means)
#   - Status: Ungauged (no local calibration)
#
# Prerequisites:
#   - setup_saxony_0p0625_1991_2020.sh has been run
#   - mhm_parameter.nml exists in runs/saxony_0p0625/nml/
#   - mhm.nml exists with correct time period
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
MINIFORGE="/data/.openclaw/workspace/miniforge"

# Saxony catchment
CATCHMENT_ID="saxony_0p0625"
CATCHMENT_NAME="Saxony"
RUN_DIR="${RUNS_DIR}/${CATCHMENT_ID}"

echo "==============================================================================="
echo "🏔️  Run Saxony Catchment (1991-2020)"
echo "==============================================================================="
echo ""
echo "📊 Catchment: ${CATCHMENT_NAME} (${CATCHMENT_ID})"
echo "📅 Period: 1991 - 2020 (30 years)"
echo "🔧 mHM Version: 5.13.2"
echo "📂 Run directory: ${RUN_DIR}"
echo ""
echo "==============================================================================="

# Check if run directory exists
if [ ! -d "${RUN_DIR}" ]; then
    echo -e "${RED}❌ Error: Run directory not found: ${RUN_DIR}${NC}"
    echo ""
    echo "Please run setup first:"
    echo "  bash ops/bin/setup_saxony_0p0625_1991_2020.sh"
    echo ""
    exit 1
fi

cd "${RUN_DIR}"

# Check for mhm_parameter.nml
if [ ! -f "nml/mhm_parameter.nml" ]; then
    echo -e "${RED}❌ Error: nml/mhm_parameter.nml not found${NC}"
    echo ""
    echo "Please run setup first:"
    echo "  bash ops/bin/setup_saxony_0p0625_1991_2020.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Found: nml/mhm_parameter.nml${NC}"

# Check for mhm.nml
if [ ! -f "nml/mhm.nml" ]; then
    echo -e "${RED}❌ Error: nml/mhm.nml not found${NC}"
    echo ""
    echo "Please create mhm.nml manually or run setup script."
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Found: nml/mhm.nml${NC}"

# Check mhm.nml for correct time period
echo ""
echo "📅 Checking mhm.nml configuration..."

# Extract start and end year from mhm.nml
START_YEAR=$(grep -i "startDate" nml/mhm.nml | head -1 | grep -oE "[0-9]{4}" | head -1)
END_YEAR=$(grep -i "endDate" nml/mhm.nml | head -1 | grep -oE "[0-9]{4}" | head -1)

if [ -n "${START_YEAR}" ] && [ -n "${END_YEAR}" ]; then
    echo "   Current: ${START_YEAR} - ${END_YEAR}"
    
    if [ "${START_YEAR}" != "1991" ] || [ "${END_YEAR}" != "2020" ]; then
        echo -e "${YELLOW}⚠️  Time period mismatch! Expected: 1991-2020${NC}"
        echo ""
        echo "Please update nml/mhm.nml:"
        echo "  startDate = \"1991-01-01\""
        echo "  endDate   = \"2020-12-31\""
        echo ""
        read -p "Continue anyway? [y/N]: " confirm
        if [ "${confirm}" != "y" ] && [ "${confirm}" != "Y" ]; then
            echo "Aborted."
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Time period correct: 1991-2020${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not parse time period from mhm.nml${NC}"
    echo "   Please verify manually."
fi

echo ""

# Check input data
echo "📂 Checking input data..."
INPUT_DIRS=("input/meteo" "input/morph" "input/lai" "input/latlon")
MISSING_INPUT=false

for dir in "${INPUT_DIRS[@]}"; do
    if [ -d "${dir}" ]; then
        count=$(ls -1 "${dir}" 2>/dev/null | wc -l)
        echo "   ✅ ${dir}/ (${count} files)"
    else
        echo "   ❌ ${dir}/ (missing)"
        MISSING_INPUT=true
    fi
done

if [ "${MISSING_INPUT}" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some input directories are missing.${NC}"
    echo "   The simulation may fail. Continue anyway."
    echo ""
    read -p "Continue? [y/N]: " confirm
    if [ "${confirm}" != "y" ] && [ "${confirm}" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

echo ""

# Activate miniforge Python environment (for any Python dependencies)
export PATH="${MINIFORGE}/bin:$PATH"
echo -e "${BLUE}🐍 Environment activated${NC}"
echo ""

# Run mHM
echo -e "${BLUE}🏃 Running mHM...${NC}"
echo "   Working directory: $(pwd)"
echo "   Command: mhm (from runs/ directory)"
echo ""

# Create output directory if not exists
mkdir -p output

# Execute mHM from parent directory (runs/)
cd ..
if mhm ./${CATCHMENT_ID}; then
    echo ""
    echo -e "${GREEN}✅ SUCCESS: ${CATCHMENT_NAME} simulation completed${NC}"
    
    # Return to run directory
    cd "${RUN_DIR}"
    
    # Check output files
    echo ""
    echo "📊 Output files:"
    
    if [ -d "output" ]; then
        nc_files=$(ls -1 output/*.nc 2>/dev/null | wc -l)
        echo "   📦 NetCDF files: ${nc_files}"
        
        if [ -f "output/daily_discharge.out" ]; then
            lines=$(wc -l < "output/daily_discharge.out")
            echo -e "   ✅ daily_discharge.out (${lines} lines)"
        else
            echo -e "   ⚠️  daily_discharge.out not found"
        fi
        
        if [ -f "output/daily_recharge.out" ]; then
            lines=$(wc -l < "output/daily_recharge.out")
            echo -e "   ✅ daily_recharge.out (${lines} lines)"
        fi
        
        if [ -f "output/daily_soilmoisture.out" ]; then
            lines=$(wc -l < "output/daily_soilmoisture.out")
            echo -e "   ✅ daily_soilmoisture.out (${lines} lines)"
        fi
    fi
    
    echo ""
    echo "📄 Log files:"
    if [ -f "output/mhm.log" ]; then
        echo "   ✅ output/mhm.log"
    fi
    if [ -f "mhm.log" ]; then
        echo "   ✅ mhm.log"
    fi
    
    echo ""
    echo "==============================================================================="
    echo "🎉 SIMULATION COMPLETE!"
    echo "==============================================================================="
    echo ""
    echo "📂 Output directory: ${RUN_DIR}/output/"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Check output files: ls -la ${RUN_DIR}/output/"
    echo "  2. View discharge: cat ${RUN_DIR}/output/daily_discharge.out | head -20"
    echo "  3. Run analysis: bash ${WORKSPACE}/ops/bin/worker_once.sh"
    echo "  4. View dashboard: http://187.124.13.209:8502"
    echo ""
    
    exit 0
else
    # Return to run directory
    cd "${RUN_DIR}"
    
    echo ""
    echo -e "${RED}❌ ERROR: ${CATCHMENT_NAME} simulation failed${NC}"
    echo ""
    echo "Check logs for details:"
    echo "  - ${RUN_DIR}/mhm.log"
    echo "  - ${RUN_DIR}/output/mhm.log"
    echo ""
    echo "Common issues:"
    echo "  - Missing input data"
    echo "  - Wrong time period in mhm.nml"
    echo "  - Invalid parameter values in mhm_parameter.nml"
    echo ""
    exit 1
fi
