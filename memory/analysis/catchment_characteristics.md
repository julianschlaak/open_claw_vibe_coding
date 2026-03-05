# Catchment Characteristics (Analysis Set)

Date: 2026-03-05  
Dataset period: 2005-01-01 to 2020-12-31 (5844 daily steps)

## Overview table (5 target catchments)

| Catchment | Gauge ID | KGE | Priority | SMI drought days | MDI drought days |
|---|---:|---:|---|---:|---:|
| Chemnitz2_0p0625 | 0090410700 | 0.745 | high | 1095 | 446 |
| Wesenitz2_0p0625 | 0090410480 | 0.729 | high | 1095 | 504 |
| Parthe_0p0625 | 0090411280 | 0.220 | low | 1095 | 642 |
| Wyhra_0p0625 | 0090412470 | 0.239 | low | 1095 | 558 |
| saxony_0p0625 | 0090410340 | 0.114 | low | 1095 | 450 |

Source:
- `analysis/scripts/01_load_data.py` (`CATCHMENTS`)
- `analysis/results/<catchment>/indices_summary.json`

## Interpretation: Why are some catchments "good" and others "poor"?

Using KGE as model-performance indicator:
- High-performance group: Chemnitz2_0p0625, Wesenitz2_0p0625 (`KGE > 0.7`)
- Lower-performance group: Parthe_0p0625, Wyhra_0p0625, saxony_0p0625

Plausible drivers (to verify with physiographic metadata):
- Stronger anthropogenic regulation, abstractions, or ungauged inflows.
- Catchment heterogeneity not represented by model setup/parameter transfer.
- Input/forcing uncertainty and local routing/groundwater dynamics.

Important:
- Catchment size, land use, and soil type are not yet stored in this repository in structured form.
- Add these attributes before final manuscript interpretation.

## Data gap to close

Add a machine-readable table with:
- Area
- Dominant land use
- Main soil classes
- Mean elevation/slope
- Hydrogeology descriptors

Recommended storage location:
- `memory/analysis/catchment_attributes.csv`
