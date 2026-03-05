# Pipeline Usage Guide

This document describes the reproducible analysis pipeline for PhD Paper #1.

## Repository root

`/docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding`

## Environment

```bash
cd /docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding
export PATH="/docker/openclaw-1lxa/data/.openclaw/workspace/miniforge/bin:$PATH"
```

## Pipeline steps

1. Load and harmonize inputs
```bash
python analysis/scripts/01_load_data.py --catchment <catchment>
```

2. Compute drought indices
```bash
python analysis/scripts/02_compute_indices.py --catchment <catchment>
```

3. Create standard plots (01-11)
```bash
python analysis/scripts/03_create_plots.py --catchment <catchment>
```

4. Create advanced scientific plots (A-F)
```bash
python analysis/scripts/04_advanced_analysis.py --catchment <catchment>
```

5. Optional EDID/EDII validation
```bash
python analysis/scripts/05_edid_validation.py --country DE --year-from 2005 --year-to 2020
```

## Typical run for all core catchments

```bash
for c in Chemnitz2_0p0625 Wesenitz2_0p0625 Parthe_0p0625 Wyhra_0p0625 saxony_0p0625; do
  python analysis/scripts/01_load_data.py --catchment "$c"
  python analysis/scripts/02_compute_indices.py --catchment "$c"
  python analysis/scripts/03_create_plots.py --catchment "$c"
  python analysis/scripts/04_advanced_analysis.py --catchment "$c"
done
```

## Outputs

- `analysis/results/<catchment>/drought_data.parquet`
- `analysis/results/<catchment>/drought_indices.parquet`
- `analysis/plots/<catchment>/` (11 standard plots)
- `analysis/plots/<catchment>/advanced/` (6 advanced plots)
- `analysis/results/edid_validation/` (optional EDID/EDII comparison tables)

## Notes

- `qobs` is loaded from CAMELS-DE where available, otherwise from `daily_discharge.out` fallback.
- NetCDF (`*.nc`) and large rasters are intentionally not versioned.
