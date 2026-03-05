# Drought Indices Methodology (Paper #1)

Date: 2026-03-05

## Scope

This project computes percentile-based and standardized drought indices for 2005-01-01 to 2020-12-31 at catchment scale.

## Core percentile-based indices

1. `SMI` (Soil Moisture Index)
- Input: `sm_lall` (volumetric soil moisture).
- Method: empirical calendar percentile via `calendar_percentile()`.
- Daily data uses day-of-year groups, removing seasonal bias.

2. `R-Pctl` (Recharge Percentile)
- Input: `recharge`.
- Method: same calendar percentile logic.

3. `Q-Pctl` (Discharge Percentile)
- Input priority: `qobs` if available, else `qsim`.
- Method: same calendar percentile logic.

4. `MDI` (Matrix Drought Index)
- Weighted composite:
  - `0.4 * SMI`
  - `0.3 * R-Pctl` lagged by ~30 days
  - `0.3 * Q-Pctl` lagged by ~60 days
- Implemented in `calculate_mdi()`.

## Drought classes

Applied to percentile indices (`SMI`, `R-Pctl`, `Q-Pctl`, `MDI`):
- `extreme_drought`: < 2
- `severe_drought`: < 5
- `moderate_drought`: < 10
- `mild_drought`: < 20
- `normal_or_wet`: >= 20

## Standardized comparison indices

1. `SPI-1/3/6`
- Gamma fit on accumulated precipitation, mapped to standard normal.

2. `SPEI-1/3/6`
- Uses water balance `P - PET`, log-logistic fit, mapped to standard normal.

3. `SDI-3/6`
- Standardized accumulated discharge.

## Implementation references

- Code: `analysis/scripts/02_compute_indices.py`
- SMI method check: `memory/research/smi_methodology.md`

## Percentile vs standardized methods

Percentile-based strengths:
- Season-aware by construction (DOY/month grouping).
- Robust to non-normal and skewed distributions.
- Easy threshold communication (e.g., <20% drought).

Percentile-based limitations:
- In-sample ranking depends on chosen reference period.
- No direct probabilistic return-period interpretation.

Standardized strengths:
- Comparable scale across variables/regions.
- Classical drought literature compatibility (SPI/SPEI/SDI).

Standardized limitations:
- Distribution-fit sensitivity (especially tails).
- Requires stronger assumptions than empirical ranks.
