#!/bin/bash
# Run Saxony simulation for 1971-2020
set -euo pipefail

WORKSPACE="/data/.openclaw/workspace/open_claw_vibe_coding"
RUN_DIR="${WORKSPACE}/code/mhm/runs/saxony_0p0625"
CATCHMENT_ID="saxony_0p0625"
MINIFORGE="/data/.openclaw/workspace/miniforge"

if [ ! -d "${RUN_DIR}" ]; then
  echo "Run directory missing: ${RUN_DIR}"
  echo "Run setup first: bash ${WORKSPACE}/ops/bin/setup_saxony_0p0625_1971_2020.sh"
  exit 1
fi

cd "${RUN_DIR}"

for f in nml/mhm.nml nml/mhm_parameter.nml; do
  if [ ! -f "${f}" ]; then
    echo "Missing ${f}"
    exit 1
  fi
done

# Enforce forward simulation mode and period
awk '/eval_Per\(1\)%yStart/{print;found=1} END{if(!found) exit 1}' nml/mhm.nml >/dev/null
sed -i -E 's|^[[:space:]]*optimize[[:space:]]*=.*|optimize = .False.|I' nml/mhm.nml
sed -i -E 's|^[[:space:]]*eval_Per\(1\)%yStart[[:space:]]*=.*|eval_Per(1)%yStart = 1971|' nml/mhm.nml
sed -i -E 's|^[[:space:]]*eval_Per\(1\)%yEnd[[:space:]]*=.*|eval_Per(1)%yEnd   = 2020|' nml/mhm.nml

# Verify LAI grid matches DEM header (ncols/nrows/xll/yll/cellsize/nodata)
if ! cmp -s <(head -n 6 input/morph/dem.asc) <(head -n 6 input/morph/LAI_class.asc); then
  echo "LAI_class.asc header does not match dem.asc. Re-run setup."
  exit 1
fi

# Ensure project-root namelist links
ln -sfn nml/mhm.nml mhm.nml
ln -sfn nml/mhm_parameter.nml mhm_parameter.nml
[ -f nml/mhm_outputs.nml ] && ln -sfn nml/mhm_outputs.nml mhm_outputs.nml

# Ensure gauge file link exists and is valid
GAUGE_LINK="input/gauge/90410340.day"
GAUGE_SRC_A="/docker/openclaw-1lxa/data/camles_de_sax/90410340/90410340.day"
GAUGE_SRC_B="/docker/openclaw-1lxa/data/camles_de_sax/90410340.day"
if [ ! -f "${GAUGE_LINK}" ]; then
  mkdir -p input/gauge
  if [ -f "${GAUGE_SRC_A}" ]; then
    ln -sfn "${GAUGE_SRC_A}" "${GAUGE_LINK}"
  elif [ -f "${GAUGE_SRC_B}" ]; then
    ln -sfn "${GAUGE_SRC_B}" "${GAUGE_LINK}"
  else
    echo "Gauge file missing: ${GAUGE_LINK}"
    echo "Tried: ${GAUGE_SRC_A} and ${GAUGE_SRC_B}"
    exit 1
  fi
fi

# Resolve mHM executable robustly
export PATH="${MINIFORGE}/bin:${PATH}"
if [ -x "${MINIFORGE}/bin/mhm" ]; then
  MHM_CMD="${MINIFORGE}/bin/mhm"
elif command -v mhm >/dev/null 2>&1; then
  MHM_CMD="mhm"
else
  echo "mhm executable not found."
  echo "Expected at: ${MINIFORGE}/bin/mhm"
  exit 1
fi

echo "Running mHM for ${CATCHMENT_ID} (1971-2020)..."
cd ..
"${MHM_CMD}" "./${CATCHMENT_ID}"
cd "${RUN_DIR}"

echo "Done. Key outputs:"
ls -lh output/daily_discharge.out output/*.nc 2>/dev/null || true
