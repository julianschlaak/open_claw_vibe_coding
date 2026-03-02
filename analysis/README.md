# Drought Analysis Pipeline

Generates hydrological drought indicators from mHM outputs:
- `SMI` percentile from `SM_Lall`
- standardized `SSI` from SMI percentiles
- recharge percentile from `recharge`
- runoff percentile from `Q`
- discharge percentile from monthly mean `Qsim_*` in `discharge.nc`

## Run

```bash
/docker/openclaw-1lxa/data/.openclaw/workspace/miniforge/bin/python -B analysis/scripts/drought_pipeline.py
```

Run from repository root:
`/docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding`

## Outputs

- `analysis/results/monthly_drought_indices.csv`
- `analysis/results/daily_discharge_qsim.csv`
- `analysis/results/drought_summary.csv`
- `analysis/plots/drought_indices_timeseries.png`
- `analysis/plots/heatmap_smi_percent.png`
- `analysis/plots/heatmap_recharge_percent.png`
- `analysis/plots/heatmap_discharge_percent.png`
