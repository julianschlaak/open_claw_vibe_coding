#!/bin/bash
# Setup Saxony run for 1971-2020 (wrapper + hardening)
set -euo pipefail

WORKSPACE="/data/.openclaw/workspace/open_claw_vibe_coding"
RUN_DIR="${WORKSPACE}/code/mhm/runs/saxony_0p0625"
LEGACY_SETUP="${WORKSPACE}/ops/bin/setup_saxony_0p0625_1991_2020.sh"

if [ -x "${LEGACY_SETUP}" ] || [ -f "${LEGACY_SETUP}" ]; then
  echo "[1/4] Running base Saxony setup..."
  bash "${LEGACY_SETUP}"
else
  echo "[1/4] Legacy setup script not found, continuing with patch-only mode."
fi

echo "[2/4] Ensuring project links and directories..."
mkdir -p "${RUN_DIR}"/nml "${RUN_DIR}"/input/{gauge,common} "${RUN_DIR}"/output "${RUN_DIR}"/restart
for f in mhm.nml mhm_parameter.nml; do
  if [ -f "${RUN_DIR}/${f}" ] && [ ! -f "${RUN_DIR}/nml/${f}" ]; then
    cp "${RUN_DIR}/${f}" "${RUN_DIR}/nml/${f}"
  fi
  if [ -e "${RUN_DIR}/${f}" ] && [ ! -L "${RUN_DIR}/${f}" ]; then
    mv "${RUN_DIR}/${f}" "${RUN_DIR}/${f}.bak.$(date +%Y%m%d_%H%M%S)"
  fi
  ln -sfn "nml/${f}" "${RUN_DIR}/${f}"
done
if [ -f "${RUN_DIR}/mhm_outputs.nml" ] && [ ! -f "${RUN_DIR}/nml/mhm_outputs.nml" ]; then
  cp "${RUN_DIR}/mhm_outputs.nml" "${RUN_DIR}/nml/mhm_outputs.nml"
fi
if [ -f "${RUN_DIR}/nml/mhm_outputs.nml" ]; then
  ln -sfn "nml/mhm_outputs.nml" "${RUN_DIR}/mhm_outputs.nml"
fi

echo "[3/4] Fixing gauge + LAI grid consistency..."
GAUGE_SRC_A="/docker/openclaw-1lxa/data/camles_de_sax/90410340/90410340.day"
GAUGE_SRC_B="/docker/openclaw-1lxa/data/camles_de_sax/90410340.day"
if [ -f "${GAUGE_SRC_A}" ]; then
  ln -sfn "${GAUGE_SRC_A}" "${RUN_DIR}/input/gauge/90410340.day"
elif [ -f "${GAUGE_SRC_B}" ]; then
  ln -sfn "${GAUGE_SRC_B}" "${RUN_DIR}/input/gauge/90410340.day"
else
  echo "Gauge source file not found for 90410340.day"
  exit 1
fi
for f in LAI_classdefinition.txt geology_classdefinition.txt soil_classdefinition.txt; do
  if [ ! -f "${RUN_DIR}/input/common/${f}" ]; then
    cp "${WORKSPACE}/code/mhm/catchment_custom/input/morph/${f}" "${RUN_DIR}/input/common/${f}"
  fi
done

/data/.openclaw/workspace/miniforge/bin/python - << 'PY'
from pathlib import Path
import numpy as np
run_dir = Path('/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/runs/saxony_0p0625')
dem = run_dir / 'input' / 'morph' / 'dem.asc'
lai = run_dir / 'input' / 'morph' / 'LAI_class.asc'

with open(dem, 'r') as f:
    hdr = [next(f) for _ in range(6)]
dem_data = np.loadtxt(dem, skiprows=6)
nodata = float(hdr[5].split()[-1])
lai_data = np.where(np.isclose(dem_data, nodata), nodata, 1.0)

with open(lai, 'w') as f:
    f.writelines(hdr)
    np.savetxt(f, lai_data, fmt='%.0f')

print(f'Wrote LAI_class.asc with shape {lai_data.shape} matching DEM')
PY

echo "[4/4] Setting simulation period and mode (1971-2020, optimize=false)..."
NML="${RUN_DIR}/nml/mhm.nml"
sed -i -E 's|^[[:space:]]*optimize[[:space:]]*=.*|optimize = .False.|I' "${NML}"
sed -i -E 's|^[[:space:]]*eval_Per\(1\)%yStart[[:space:]]*=.*|eval_Per(1)%yStart = 1971|' "${NML}"
sed -i -E 's|^[[:space:]]*eval_Per\(1\)%yEnd[[:space:]]*=.*|eval_Per(1)%yEnd   = 2020|' "${NML}"
sed -i -E 's|^[[:space:]]*Gauge_id\(1,1\)[[:space:]]*=.*|Gauge_id(1,1)       = 90410340|' "${NML}"
sed -i -E 's|^[[:space:]]*gauge_filename\(1,1\)[[:space:]]*=.*|gauge_filename(1,1) = "90410340.day"|' "${NML}"

rg -n "optimize|eval_Per\(1\)%yStart|eval_Per\(1\)%yEnd|Gauge_id\(1,1\)|gauge_filename\(1,1\)" "${NML}" -N
head -n 6 "${RUN_DIR}/input/morph/LAI_class.asc"

echo ""
echo "Setup complete: ${RUN_DIR}"
echo "Run next: bash ${WORKSPACE}/ops/bin/run_saxony_0p0625_1971_2020.sh"
