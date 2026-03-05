# SMI Methodology Check (UFZ Drought Monitor vs. Project Implementation)

Date: 2026-03-05  
Project: PhD Paper #1 (Percentile-based MDI)

## 1. What UFZ Drought Monitor uses (method summary)

The UFZ/German Drought Monitor framework is percentile-based and season-aware for soil moisture drought classification.  
Core idea: soil moisture conditions are assessed relative to climatology, not by absolute values.

References used:
- UFZ Drought Monitor (method context, product definition):  
  https://www.ufz.de/index.php?en=37937
- HESS paper on German/UFZ drought monitor development and methodology context:  
  https://hess.copernicus.org/articles/25/565/2021/
- UFZ publication list entry referencing soil-moisture drought monitoring in Germany:  
  https://www.ufz.de/index.php?en=20939&pub_id=21750

## 2. What our code currently does

File: `analysis/scripts/02_compute_indices.py`  
Function: `calendar_percentile(dates, values)`

Current logic:
- Determines temporal resolution from median timestep.
- Daily data: percentile is computed within each day-of-year group (`dayofyear`).
- Monthly/coarser data: percentile is computed within each month group.
- Uses empirical rank (`rank(..., pct=True) * 100`), no parametric distribution assumption.

This means:
- We **do compare each day to its seasonal peers**, not to the full time series.
- We **do not** compute one global percentile over all days of the year.

## 3. Verification result for requested question

Question: "Perzentil pro Day-of-Year über alle Jahre (korrekt) oder über gesamte Zeitreihe (falsch)?"

Result:
- Our implementation is **Day-of-Year based** for daily data (correct seasonal logic).
- Therefore, **no bug fix is required** for the specific DOY-vs-full-series issue.

## 4. Important methodological differences to document

Even though the DOY logic is correct, our implementation is still a simplified variant compared with operational UFZ products:
- No dedicated long climatological reference period (we use available model period).
- No additional temporal smoothing or product-specific post-processing steps.
- Percentile estimation is empirical rank-based in-sample.

These are scientific design choices, not coding errors. They should be explicitly reported in the methods section of the paper.

## 5. Quick sanity check from current outputs

Chemnitz test (`analysis/results/Chemnitz2_0p0625/drought_indices.parquet`):
- SMI range: `6.25 - 100.00`

Interpretation:
- SMI is finite and varying (not all NaN, not constant), consistent with functioning percentile computation.
