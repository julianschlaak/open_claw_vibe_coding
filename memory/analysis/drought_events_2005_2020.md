# Drought Events 2005-2020 (Catchment Summary)

Date: 2026-03-05  
Method basis: MDI (`<20` = drought day), from `drought_indices.parquet`

## Key result

The strongest multi-year event across all five catchments is 2018-2020.  
This signal is robust in both low and high KGE groups.

## Top dry years by mean MDI

| Catchment | 1st driest | 2nd driest | 3rd driest |
|---|---|---|---|
| Chemnitz2_0p0625 | 2018 (32.5) | 2020 (33.0) | 2019 (34.3) |
| Wesenitz2_0p0625 | 2020 (20.8) | 2019 (29.2) | 2018 (31.9) |
| Parthe_0p0625 | 2020 (16.8) | 2019 (18.2) | 2018 (37.2) |
| Wyhra_0p0625 | 2020 (19.2) | 2019 (25.2) | 2018 (35.0) |
| saxony_0p0625 | 2020 (22.3) | 2019 (28.9) | 2018 (37.1) |

## Highest MDI drought-day years

| Catchment | Top years (drought days/year) |
|---|---|
| Chemnitz2_0p0625 | 2018: 144, 2019: 101, 2020: 91 |
| Wesenitz2_0p0625 | 2020: 192, 2018: 166, 2019: 108 |
| Parthe_0p0625 | 2020: 257, 2019: 219, 2018: 151 |
| Wyhra_0p0625 | 2020: 210, 2019: 139, 2018: 138 |
| saxony_0p0625 | 2020: 178, 2018: 128, 2019: 114 |

## Chronology notes

- 2005-2010: mixed conditions, local events (e.g., 2006 in several basins).
- 2011-2017: intermittent drought periods, generally less persistent than post-2018.
- 2018-2020: dominant drought phase in all catchments, strongest persistence and lowest MDI means.

## Event benchmark note (2003)

The current simulation/analysis window starts at 2005-01-01, so 2003 cannot be validated directly in this dataset.

## EDID comparison status

Not performed yet in this step.  
For manuscript-level validation, compare annual MDI drought-day counts with EDID impact counts by region/year.
