#!/bin/bash
#===============================================================================
# Run All 6 Catchments (1991-2020) with Recommended Parameter Set
# 
# Usage: bash run_all_6_catchments_1991_2020.sh
# 
# This script runs mHM for all 6 calibrated catchments using the
# recommended parameter set from DDS analysis (no calibration, just simulation).
#
# Catchments:
#   1. Parthe_0p0625
#   2. Goeltzsch2_0p0625
#   3. Chemnitz2_0p0625
#   4. Wesenitz2_0p0625
#   5. Wyhra_0p0625
#   6. Zwoenitz1_0p0625
#
# Period: 1991-2020 (30 years)
#
# Prerequisites:
#   - recommended_params.csv exists in dashboard_saxony/utils/
#   - mHM 5.13.2 available in container
#   - Input data available for all catchments
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
MHM_RE_CRIT="${WORKSPACE}/code/mhm_re_crit"
RUNS_DIR="${MHM_RE_CRIT}/runs"
RECOMMENDED_PARAMS_CSV="${WORKSPACE}/dashboard_saxony/utils/recommended_params.csv"
MINIFORGE="/data/.openclaw/workspace/miniforge"

# Catchment list
CATCHMENTS=(
    "parthe_0p0625"
    "goeltzsch2_0p0625"
    "chemnitz2_0p0625"
    "wesenitz2_0p0625"
    "wyhra_0p0625"
    "zwoenitz1_0p0625"
)

# Time period
START_YEAR=1991
END_YEAR=2020

echo "==============================================================================="
echo "🚀 mHM Simulation: All 6 Catchments (1991-2020)"
echo "==============================================================================="
echo ""
echo "📊 Catchments: ${#CATCHMENTS[@]}"
printf "   - %s\n" "${CATCHMENTS[@]}"
echo ""
echo "📅 Period: ${START_YEAR} - ${END_YEAR} (30 years)"
echo ""
echo "🔧 mHM Version: 5.13.2"
echo "📂 Workspace: ${WORKSPACE}"
echo ""
echo "==============================================================================="

# Check if recommended_params.csv exists and ask user
if [ -f "${RECOMMENDED_PARAMS_CSV}" ]; then
    echo -e "${GREEN}✅ Found: ${RECOMMENDED_PARAMS_CSV}${NC}"
    echo ""
    echo "🤔 Parameter source selection:"
    echo "   1) Use FinalParam.nml from DDS calibration (recommended, catchment-specific)"
    echo "   2) Use recommended_params.csv (GLOBAL parameters from statistical analysis)"
    echo ""
    read -p "Choose option [1-2] (default: 1): " param_choice
    
    if [ "${param_choice}" = "2" ]; then
        echo ""
        echo "🔧 Generating mhm_parameter.nml from recommended_params.csv..."
        echo ""
        
        # Run Python script to generate NML files
        export PATH="${MINIFORGE}/bin:$PATH"
        if python3 "${WORKSPACE}/ops/bin/generate_recommended_param_nml.py"; then
            echo ""
            echo -e "${GREEN}✅ Generated recommended parameter files${NC}"
            USE_DDS_PARAMS=false
        else
            echo ""
            echo -e "${RED}❌ Failed to generate recommended parameters${NC}"
            echo "   Falling back to FinalParam.nml files"
            USE_DDS_PARAMS=true
        fi
    else
        echo -e "${GREEN}✅ Using FinalParam.nml files from DDS calibration${NC}"
        USE_DDS_PARAMS=true
    fi
else
    echo -e "${YELLOW}⚠️  Warning: ${RECOMMENDED_PARAMS_CSV} not found${NC}"
    echo "   Using FinalParam.nml files from DDS calibration"
    echo ""
    USE_DDS_PARAMS=true
fi

# Activate miniforge Python environment
export PATH="${MINIFORGE}/bin:$PATH"
echo -e "${BLUE}🐍 Python environment activated${NC}"
echo ""

#-------------------------------------------------------------------------------
# Function: Run single catchment
#-------------------------------------------------------------------------------
run_catchment() {
    local catchment=$1
    local run_dir="${RUNS_DIR}/${catchment}"
    
    echo "==============================================================================="
    echo "🏞️  Catchment: ${catchment}"
    echo "==============================================================================="
    echo ""
    
    # Check if run directory exists
    if [ ! -d "${run_dir}" ]; then
        echo -e "${RED}❌ Error: Run directory not found: ${run_dir}${NC}"
        echo "   Skipping ${catchment}..."
        echo ""
        return 1
    fi
    
    cd "${run_dir}"
    
    # Check for mhm_parameter.nml (already generated or from FinalParam)
    if [ -f "nml/mhm_parameter.nml" ]; then
        echo -e "${GREEN}✅ Found: nml/mhm_parameter.nml${NC}"
    else
        echo -e "${RED}❌ Error: nml/mhm_parameter.nml not found${NC}"
        echo "   Skipping ${catchment}..."
        echo ""
        return 1
    fi
    
    echo ""
    
    # Check mhm.nml for correct time period
    echo "📅 Checking mhm.nml configuration..."
    
    # Extract start and end year from mhm.nml (eval_Per format)
    local start_year=$(grep -i "yStart" nml/mhm.nml | head -1 | awk '{print $NF}')
    local end_year=$(grep -i "yEnd" nml/mhm.nml | head -1 | awk '{print $NF}')
    
    echo "   Current: ${start_year} - ${end_year}"
    
    if [ "${start_year}" != "${START_YEAR}" ] || [ "${end_year}" != "${END_YEAR}" ]; then
        echo -e "${YELLOW}⚠️  Time period mismatch! Expected: ${START_YEAR}-${END_YEAR}${NC}"
        echo "   Please update nml/mhm.nml manually:"
        echo "   - eval_Per(1)%yStart = ${START_YEAR}"
        echo "   - eval_Per(1)%yEnd   = ${END_YEAR}"
        echo ""
        echo "   Skipping ${catchment}..."
        echo ""
        return 1
    else
        echo -e "${GREEN}✅ Time period correct: ${START_YEAR}-${END_YEAR}${NC}"
    fi
    
    echo ""
    
    # Run mHM
    echo -e "${BLUE}🏃 Running mHM...${NC}"
    echo "   Working directory: $(pwd)"
    echo "   Command: mhm ./${catchment}"
    echo ""
    
    # Execute mHM (run from parent directory)
    cd ..
    if mhm ./${catchment}; then
        echo ""
        echo -e "${GREEN}✅ SUCCESS: ${catchment} completed${NC}"
        
        # Check output files
        if [ -d "${catchment}/output" ]; then
            local output_files=$(ls -1 ${catchment}/output/*.nc 2>/dev/null | wc -l)
            echo "   Output files: ${output_files} .nc files"
        fi
        
        if [ -f "${catchment}/output/daily_discharge.out" ]; then
            echo -e "${GREEN}✅ Found: daily_discharge.out${NC}"
        fi
        
        echo ""
    else
        echo ""
        echo -e "${RED}❌ ERROR: ${catchment} failed${NC}"
        echo "   Check logs in: ${run_dir}/output/"
        echo ""
        cd "${run_dir}"
        return 1
    fi
    
    # Return to run directory
    cd "${run_dir}"
    echo ""
    return 0
}

#-------------------------------------------------------------------------------
# Main execution
#-------------------------------------------------------------------------------

echo "📋 Starting simulations..."
echo ""

# Counter for success/failure
SUCCESS=0
FAILED=0
SKIPPED=0

# Run all catchments
for catchment in "${CATCHMENTS[@]}"; do
    if run_catchment "${catchment}"; then
        ((SUCCESS++))
    else
        if [ $? -eq 1 ]; then
            ((FAILED++))
        else
            ((SKIPPED++))
        fi
    fi
    
    echo ""
    echo "⏸️  Waiting 5 seconds before next catchment..."
    sleep 5
    echo ""
done

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------

echo "==============================================================================="
echo "📊 SIMULATION SUMMARY"
echo "==============================================================================="
echo ""
echo "✅ Successful: ${SUCCESS}"
echo "❌ Failed:     ${FAILED}"
echo "⚠️  Skipped:    ${SKIPPED}"
echo ""
echo "Total: ${#CATCHMENTS[@]} catchments"
echo ""

if [ ${SUCCESS} -eq ${#CATCHMENTS[@]} ]; then
    echo -e "${GREEN}🎉 All catchments completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Check output files in: ${RUNS_DIR}/<catchment>/output/"
    echo "  2. Run analysis: bash ${WORKSPACE}/ops/bin/worker_once.sh"
    echo "  3. View dashboard: http://187.124.13.209:8502"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some catchments failed or were skipped${NC}"
    echo ""
    echo "Check logs for details."
    echo ""
    exit 1
fi
