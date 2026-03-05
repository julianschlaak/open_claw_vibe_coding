# PhD Paper #1: Percentile-Based Multi-Component Drought Index

**Title:** "A Percentile-Based Multi-Component Drought Index for Hydrological Drought Monitoring in Central Europe"  
**Author:** Julian Schlaak  
**Status:** Draft complete (March 2026)  
**Target Journal:** HESS or Journal of Hydrology

## Quick Start

```bash
cd /docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding
export PATH="/docker/openclaw-1lxa/data/.openclaw/workspace/miniforge/bin:$PATH"

python analysis/scripts/01_load_data.py --catchment <name>
python analysis/scripts/02_compute_indices.py --catchment <name>
python analysis/scripts/03_create_plots.py --catchment <name>
python analysis/scripts/04_advanced_analysis.py --catchment <name>
```

## Repository Structure

- `paper/draft_v1/` — manuscript draft (sections 01-06)
- `analysis/scripts/` — pipeline scripts (`01` to `05` + helpers)
- `analysis/plots/` — standard and advanced figures
- `analysis/results/` — reproducible result tables and parquet files
- `memory/research/` — methodology notes
- `memory/analysis/` — catchment/event analyses
- `analysis/PIPELINE_README.md` — full pipeline usage guide

## Reproducing Paper Results

See `analysis/PIPELINE_README.md` for full instructions.

## Data Sources

- mHM 5.13.2: own simulations (soil moisture, recharge, discharge)
- CAMELS-DE: observed streamflow (Addor et al., 2018)
- EDID/EDII: drought impacts (DOI: 10.6094/UNIFR/230922)
- DWD: precipitation forcing
