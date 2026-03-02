# OpenClaw Vibe Coding - Hydrological Drought Analysis Framework

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![mHM 5.13.2](https://img.shields.io/badge/mHM-5.13.2-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A reproducible workflow for hydrological drought analysis using mHM simulations, standardized drought indices, and an OpenClaw-Codex automation bridge.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Core Innovation](#core-innovation)
3. [Feature Set](#feature-set)
4. [System Architecture](#system-architecture)
5. [Repository Layout](#repository-layout)
6. [Requirements](#requirements)
7. [Installation](#installation)
8. [Bridge Initialization](#bridge-initialization)
9. [Running mHM Simulations](#running-mhm-simulations)
10. [Running Analysis Pipelines](#running-analysis-pipelines)
11. [Submitting Bridge Jobs](#submitting-bridge-jobs)
12. [Output Structure](#output-structure)
13. [Result Interpretation](#result-interpretation)
14. [Examples](#examples)
15. [Troubleshooting](#troubleshooting)
16. [Quality Assurance](#quality-assurance)
17. [Credits](#credits)
18. [References](#references)

## Project Overview

This project combines physically-based hydrological simulation with post-processing and drought diagnostics.

The workflow has three layers:

- Simulation layer: mHM 5.13.2 runs domain-specific hydrological simulations.
- Analysis layer: Python pipelines compute drought indicators and produce figures.
- Operations layer: OpenClaw-Codex bridge executes queued jobs in a serialized and fault-tolerant way.

The framework currently supports:

- `test_domain` for short-run validation and method checks.
- `catchment_custom` for long-run analysis (1991-2020 expected target window).

## Core Innovation

The framework extends classic single-variable drought diagnostics by introducing an integrated matrix perspective:

- Soil moisture response (SMI/SSI-like diagnostics)
- Recharge deficits
- Streamflow deficits
- Lag-aware interpretation of coupled hydro-meteorological dynamics

The Matrix Drought Index (MDI) uses weighted components and lag information to better represent process connectivity between compartments.

## Feature Set

- Standard drought pipeline with 8 core plots per catchment.
- Advanced pipeline with lag-correlation and matrix-index plots.
- Flat plot structure per catchment for easy publication export.
- CSV output for downstream statistics and reproducibility.
- Markdown reporting structure for transparent interpretation.
- Job queue + worker bridge for deterministic automation.

## System Architecture

### 1) OpenClaw-Codex Bridge

Bridge files live in `ops/` and provide:

- `ops/jobs/` queue input
- `ops/bin/worker_once.sh` serial worker
- retry logic (3 attempts, exponential backoff)
- job schema validation and invalid-job quarantine
- runtime logs in `ops/logs/`
- status files in `ops/status/`

Supported job types:

- `healthcheck`
- `run_mhm`
- `run_analysis`
- `verify`
- `commit_push`

### 2) mHM Integration

- mHM version: 5.13.2
- Domain setups:
  - `code/mhm/test_domain/`
  - `code/mhm/catchment_custom/`
- Typical output files:
  - `mHM_Fluxes_States.nc`
  - `mRM_Fluxes_States.nc`
  - `discharge.nc`
  - `daily_discharge.out`

### 3) Analysis Pipelines

- `analysis/scripts/drought_pipeline.py`
  - standard diagnostics and core figure set
- `analysis/scripts/drought_analysis_advanced.py`
  - lag analysis and matrix drought index

## Repository Layout

```text
open_claw_vibe_coding/
├── README.md
├── analysis/
│   ├── plots/
│   │   ├── test_domain/
│   │   └── catchment_custom/
│   ├── results/
│   │   ├── test_domain/
│   │   └── catchment_custom/
│   ├── report/
│   └── scripts/
├── code/
│   └── mhm/
│       ├── test_domain/
│       └── catchment_custom/
├── model/
│   └── mhm/
└── ops/
    ├── bin/
    ├── examples/
    ├── jobs/
    ├── logs/
    └── status/
```

## Requirements

- Linux host with Docker
- Access to container `openclaw-1lxa-openclaw-1`
- Git + SSH access for push operations
- Python 3.11 environment with:
  - `numpy`
  - `pandas`
  - `scipy`
  - `matplotlib`
  - `seaborn`
  - `netCDF4`

## Installation

### 1) Clone

```bash
git clone git@github.com:julianschlaak/open_claw_vibe_coding.git
cd open_claw_vibe_coding
```

### 2) Python Environment

Inside container:

```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
python3 -c "import numpy,pandas,scipy,matplotlib,seaborn,netCDF4; print('ok')"
```

### 3) mHM Availability

```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
mhm --version
```

### 4) Git Serial Tool

```bash
/usr/local/bin/openclaw-git-serial status --short --branch
```

## Bridge Initialization

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding
bash ops/bin/healthcheck.sh
```

Expected: all checks pass (`docker`, container, Python libs, SSH key, `openclaw-git-serial`).

## Running mHM Simulations

### Test Domain

```bash
docker exec openclaw-1lxa-openclaw-1 bash -lc '
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
cd /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm
mhm ./test_domain
'
```

### Custom Catchment

```bash
docker exec openclaw-1lxa-openclaw-1 bash -lc '
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
cd /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm
mhm ./catchment_custom
'
```

## Running Analysis Pipelines

### Standard Pipeline

```bash
docker exec openclaw-1lxa-openclaw-1 bash -lc '
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
cd /data/.openclaw/workspace/open_claw_vibe_coding/analysis/scripts
python3 drought_pipeline.py --domain test_domain
python3 drought_pipeline.py --domain catchment_custom
'
```

### Advanced Pipeline

```bash
docker exec openclaw-1lxa-openclaw-1 bash -lc '
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
cd /data/.openclaw/workspace/open_claw_vibe_coding/analysis/scripts
python3 drought_analysis_advanced.py --domain test_domain
python3 drought_analysis_advanced.py --domain catchment_custom
'
```

## Submitting Bridge Jobs

### Example: Verify Job

```bash
cat > ops/jobs/job_verify_now.json << "JSON"
{
  "job_id": "job_verify_now",
  "type": "verify",
  "params": {
    "domain": "test_domain"
  }
}
JSON

bash ops/bin/worker_once.sh
cat ops/status/job_verify_now.json
```

### Example: Analysis Job

```bash
cat > ops/jobs/job_analysis_custom.json << "JSON"
{
  "job_id": "job_analysis_custom",
  "type": "run_analysis",
  "params": {
    "domain": "catchment_custom",
    "start_year": 1991,
    "end_year": 2020
  }
}
JSON

bash ops/bin/worker_once.sh
```

## Output Structure

### Plots

`analysis/plots/<catchment>/`

Expected files per catchment:

1. `01_drought_timeseries.png`
2. `02_heatmap_smi.png`
3. `03_heatmap_recharge.png`
4. `04_heatmap_discharge.png`
5. `05_discharge_analysis.png`
6. `06_correlation_matrix.png`
7. `07_drought_duration.png`
8. `08_seasonal_boxplots.png`
9. `09_lag_correlation.png`
10. `10_matrix_drought_index.png`

### Results

`analysis/results/<catchment>/`

Typical artifacts:

- percentile time series CSVs
- intermediate index tables
- summary statistics JSON

### Reports

`analysis/report/`

- domain-specific markdown interpretation reports
- figure-by-figure scientific commentary

## Result Interpretation

### Time series

Use `01_drought_timeseries.png` to identify dry episodes and transitions.

### Heatmaps

`02-04` provide interannual and seasonal signatures.

### Discharge validation

`05_discharge_analysis.png` should include:

- Qobs (red)
- Qsim (blue)
- metrics box (KGE, r, RMSE, MAE, NSE, Bias)

### Correlation structure

`06_correlation_matrix.png` supports process-level coupling interpretation.

### Event persistence

`07_drought_duration.png` quantifies consecutive dry-period lengths.

### Seasonal vulnerability

`08_seasonal_boxplots.png` isolates month-dependent drought risk.

### Advanced diagnostics

`09` and `10` evaluate lag pathways and integrated drought severity.

## Examples

### Example A: Test Domain

Goal:

- Validate script integrity
- Verify figure completeness
- Confirm metric computation and plot annotation

### Example B: Custom Catchment (30 years)

Goal:

- Analyze long-term behavior (1991-2020)
- Compare compartment response patterns
- Extract publication-ready diagnostics

## Troubleshooting

### 1) OpenClaw tools unstable (`write`/`exec`)

Symptoms:

- intermittent tool failures
- random command execution aborts

Mitigation:

- use bridge queue (`ops/jobs/` + `worker_once.sh`)
- keep jobs small and explicit
- run `healthcheck.sh` before batch operations

### 2) Git permission errors

Symptoms:

- `insufficient permission for adding an object to repository database`

Fix in container:

```bash
chown -R node:node /data/.openclaw/workspace/open_claw_vibe_coding
rm -f /data/.openclaw/workspace/open_claw_vibe_coding/.git/index.lock
```

### 3) Push rejected (non-fast-forward)

- Pull/rebase in a clean clone, then push.
- Avoid force-push on collaborative `main`.

### 4) Missing Python modules

```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
pip install numpy pandas scipy matplotlib seaborn netCDF4
```

### 5) Missing Qobs in discharge plot

- Ensure `daily_discharge.out` exists in domain output directory.
- Check column names include both `Qobs_*` and `Qsim_*`.

### 6) Implausible soil moisture magnitude

- verify the variable source (`SWC_L01` for requested quick-fix context)
- verify divisor equals effective layer depth in mm

## Quality Assurance

Recommended verification sequence:

1. `bash ops/bin/healthcheck.sh`
2. run mHM for target domain
3. run standard and advanced pipelines
4. check 10 plots per catchment
5. check result CSV completeness
6. validate discharge plot elements
7. archive status JSON + logs

## Credits

- Hydrological model foundation: mHM team (UFZ)
- Workflow engineering and automation: project maintainers
- Bridge design: OpenClaw-Codex operational integration

## References

- Samaniego, L., Kumar, R., and collaborators: mHM model framework papers.
- Kumar, R. et al.: multiscale parameter regionalization concepts.
- Rakovec, O. et al.: hydrological model evaluation and uncertainty context.
- Related drought index literature on SMI/SSI/SDI formulation and limitations.

---

For operational use, prefer queue-based execution through the bridge over ad-hoc parallel command firing.
