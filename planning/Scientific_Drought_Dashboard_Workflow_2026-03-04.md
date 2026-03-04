# Scientifically Robust Drought Monitoring Dashboard

Date: 2026-03-04  
Project: `open_claw_vibe_coding`  
Status: Scientific design complete, implementation gated behind design approval

## Scope And Workflow Gate
This document follows the requested strict sequence:

1. LOCAL RESEARCH  
2. LITERATURE GAP CHECK  
3. DATA AVAILABILITY  
4. METHOD DESIGN  
5. QUALITY CONTROL  
6. IMPLEMENTATION DESIGN  
7. DASHBOARD DESIGN  
8. IMPLEMENTATION ROADMAP

No new coding is proposed before phases 1-7 are accepted.

---

## PHASE 1 - Local Research Synthesis (Primary Source)

Primary local sources used:
- `research/hydrological_drought_indices_review/hydrological_drought_indices_review.md`
- `research/hydrological_drought_indices_review/review_v1.0_2026-03-02.md`
- `research/hydrological_drought_indices_review/review_v2.0_deep_2026-03-02.md`
- `research/review_soil_water_modeling_europe.md`
- `analysis/scripts/drought_pipeline.py`
- `analysis/scripts/drought_analysis_advanced.py`
- `analysis/scripts/build_multi_index_monitor.py`
- `analysis/results/catchment_custom/analysis_summary.md`

### 1.1 Local Index Inventory

| Index | Type | Definition (local practice) | Required variables | Time scale | Local strengths | Local weaknesses | Typical thresholds |
|---|---|---|---|---|---|---|---|
| SPI | Meteorological | Standardized anomaly of aggregated precipitation | Precipitation | 1,3,6,12 months | Robust baseline, simple interpretation | Ignores atmospheric demand | -1 moderate, -1.5 severe, -2 extreme |
| SPEI | Meteorological/atmospheric demand | Standardized anomaly of P-PET | Precipitation, PET | 1,3,6,12 months | Captures warming effects via PET | PET method sensitivity | Same as SPI class limits |
| SMI (percentile) | Soil moisture drought | Calendar percentile of soil moisture | Soil moisture | Daily or monthly climatology | Non-parametric, robust | Not cross-region standardized | <20 severe, <10 extreme |
| SSI | Soil moisture drought | Normal-score transform of soil moisture percentile/CDF | Soil moisture | Monthly, multi-scale possible | Comparable standardized scale | Sensitive to distribution fit / tails | <-1 moderate, <-1.5 severe, <-2 extreme |
| SDI | Hydrological drought | Standardized anomaly of discharge (often percentile->z) | Discharge/runoff | Monthly, seasonal | Direct hydrological relevance | Strong routing and storage lags | <-1 moderate, <-1.5 severe, <-2 extreme |
| SRI (recharge-based) | Hydrological subsurface drought | Standardized/percentile anomaly of recharge | Recharge | Monthly | Links drought to groundwater renewal | Recharge model uncertainty | Percentiles (<20, <10) or z-score classes |
| Percentile metrics (Q5/Q10/Q20) | Event diagnostics | Quantile threshold exceedance deficits | Any hydromet variable | Flexible | Intuitive event detection, robust | Not inherently standardized | Q20 mild, Q10 severe, Q5 extreme |
| Matrix Drought Index (MDI, local prototype) | Composite/propagation | Weighted index using lagged SM, recharge, discharge | SM, recharge, discharge | Monthly | Encodes drought propagation explicitly | Weight/lag calibration needed | <0.2 extreme, <0.4 severe, <0.6 moderate |

### 1.2 Proven Local Data And Methods
- Proven monthly record for `catchment_custom`: 1991-01 to 2020-12 (30 years).
- Variables already extracted in production scripts: `precip`, `pet`, `sm`, `recharge`, `runoff`, `discharge`, `qobs`, `qsim`.
- Existing code already includes:
  - percentile-based climatologies by month/day-of-year,
  - standardized transforms (normal inverse),
  - lag/correlation analysis,
  - multi-index monitor generation (SPI/SPEI/SMI + validation metrics),
  - composite lagged matrix index prototype.

Scientific conclusion from local evidence:
The project already has a strong technical base for a multi-index hydrological drought system. The major gap is formalized scientific validation/governance, not raw computation capability.

---

## PHASE 2 - Literature Gap Check

### 2.1 Confirmed In Existing Local Review
Already covered well locally: SPI, SPEI, SMI/SSI, SDI, PDSI basics, hydrological drought propagation context, EDID context.

### 2.2 Missing/Underdeveloped In Local Materials
Indices or components to add explicitly:
- RDI (Reconnaissance Drought Index) for climate-aridity sensitivity.
- SWDI (Soil Water Deficit Index) to represent root-zone deficit directly.
- Formal multivariate drought indices (copula/PCA/Bayesian or weighted composites with calibration).
- Stronger harmonization framework between percentile and standardized indices.

### 2.3 Recommended Canonical References To Anchor Methods
- McKee et al. (1993): SPI conceptual origin.
- Vicente-Serrano et al. (2010): SPEI (`https://doi.org/10.1175/2010JCLI2909.1`).
- Van Loon (2015): Hydrological drought process framing (`https://doi.org/10.1002/wat2.1085`).
- Bachmair et al. (2016/2017 line): drought impact-function and reporting logic (`https://doi.org/10.5194/hess-21-5293-2017`).
- Zink et al. (2016/2017 line): German drought monitor/mHM operational context (already listed in local planning docs; DOI final check recommended before publication).

Scientific conclusion:
Gap-filling should focus on methodological breadth (RDI/SWDI/multivariate formalization), while retaining current robust SPI/SPEI/SMI/SSI/SDI core.

---

## PHASE 3 - Data Availability And Feasibility

### 3.1 Available Data (Observed In Code + Results)
- Precipitation: available.
- PET: available.
- Soil moisture: available (multiple soil layers and aggregated forms).
- Runoff/discharge: available.
- Recharge: available.
- Daily observed/simulated discharge for validation: available where `daily_discharge.out`/`discharge.nc` provide both.

### 3.2 Feasibility Matrix

| Index | Data need | Feasible now | Notes |
|---|---|---|---|
| SPI | P | Yes | Directly implemented |
| SPEI | P, PET | Yes | Directly implemented |
| SMI | SM | Yes | Percentile framework already present |
| SSI | SM | Yes | Implemented via percentile->normal transform; can be upgraded to explicit distribution-fit path |
| SDI | Q/discharge | Yes | Implemented |
| SRI | Recharge | Yes | Implemented as recharge percentile/standardized |
| RDI | P, PET | Yes | Can be added with low effort |
| PDSI | P, PET, AWC + water balance assumptions | Partial | Needs explicit parameterization and climate assumptions |
| SWDI | Root-zone SM and field capacity/wilting point | Partial | Needs soil hydraulic parameter harmonization |
| Multivariate index | Multiple standardized indices | Yes | Requires calibration/validation framework |

### 3.3 Recommended Scientifically Robust Implementation Set
Tier 1 (implement first): SPI, SPEI, SMI, SSI, SDI, SRI, percentile diagnostics.  
Tier 2 (after calibration): RDI, MDI (composite calibrated), SWDI.  
Tier 3 (careful methodological caveats): PDSI for comparison only.

---

## PHASE 4 - Scientific Comparison Framework

### 4.1 Hydrological-Cycle Propagation Chain
Use explicit chain:
`Precipitation -> Soil Moisture -> Recharge -> Discharge`

### 4.2 Multi-timescale Comparison
Compute all standardized climate and hydrological indices at:
- 1 month
- 3 months
- 6 months
- 12 months

Interpretation rule:
- short scales: onset detection,
- medium scales: seasonal persistence,
- long scales: hydrological memory and storage depletion.

### 4.3 Lag Analysis
- Cross-correlation per pair with lags in [-12, +12] months.
- Estimate peak-lag and confidence interval via block bootstrap.
- Report physically plausible lag windows by basin class.

### 4.4 Harmonizing Standardized And Percentile Indices
- Convert all percentiles to non-exceedance probabilities p in [0,1].
- Optional common space: z = Phi^-1(p) for comparability.
- Keep original percentile view in dashboard for practitioner interpretability.
- Publish both representations simultaneously (dual reporting standard).

---

## PHASE 5 - Quality Control And Validation Framework

### 5.1 Distribution And Fit Checks (for standardized indices)
- Candidate distributions per index (Gamma, log-logistic, empirical fallback).
- Goodness-of-fit tests: KS + Anderson-Darling.
- QQ plots by month/season.
- Parameter stability over moving windows.

### 5.2 Data Integrity Checks
- Missing data diagnostics by variable and period.
- Outlier detection: robust z-score / MAD and physical plausibility bounds.
- Temporal consistency: duplicate timestamps, irregular intervals, impossible jumps.

### 5.3 Reproducibility And Auditability
- Deterministic runs with fixed seeds where needed.
- Versioned outputs (`data hash + config + code commit`).
- Automated regression tests on index series statistics and class frequencies.

### 5.4 Index-Specific Validation
- SPI/SPEI: fit quality and tail behavior checks.
- SMI/SSI/SWDI: seasonal climatology consistency, layer consistency tests.
- SDI/SRI: compare with observed low-flow episodes and recharge deficits.
- Composite index: sensitivity analysis on weights/lags and ranking robustness.

---

## PHASE 6 - Implementation Design (Before Coding)

Target structure:

```
data_processing/
indices/
analysis/
visualization/
dashboard/
```

### 6.1 Module Responsibilities
- `data_processing/`
  - ingestion, temporal alignment, gap handling, unit normalization.
- `indices/`
  - `spi.py`, `spei.py`, `smi_ssi.py`, `sdi_sri.py`, `rdi.py`, `swdi.py`, `composite.py`.
- `analysis/`
  - lag/correlation, event extraction, uncertainty analysis, benchmark comparisons.
- `visualization/`
  - map prep, time-series builders, diagnostics plots, export-ready figures.
- `dashboard/`
  - API adapters, panel configuration, interaction logic, reproducible views.

### 6.2 Mandatory Non-Functional Requirements
- Strict schema contracts between modules.
- Unit + integration tests for every index calculator.
- Reproducible environment file and runbook.
- Scientific metadata in every output artifact.

---

## PHASE 7 - Scientific Dashboard Design

Required panels and scientific standards:

1. Spatial drought overview  
- Maps for each selected index/time scale.  
- Consistent color maps and class thresholds across indices.

2. Time series comparison  
- Multi-index overlays + uncertainty or percentile bands where applicable.  
- Dynamic windows: full record, last 30 years, selected events, custom interval.

3. Hydrological drought propagation  
- Directed chain view (`P -> SM -> Recharge -> Q`) with estimated lag labels.  
- Linked brushing to highlight shared events.

4. Extreme drought analysis  
- Threshold exceedance panel (`Q20/Q10/Q5`, `z<-1/-1.5/-2`).  
- Event duration, severity, and recovery diagnostics.

5. Index comparison diagnostics  
- Correlation heatmaps, lag-correlation curves, scatter with density, consistency matrix.

Scientific visualization standards:
- Perceptually uniform, colorblind-safe palettes.
- Explicit units and reference period labels on every axis/panel.
- No mixed thresholds without visible conversion rules.
- Exportable figure metadata for manuscript reproducibility.

---

## PHASE 8 - Implementation Roadmap (Coding Starts Here)

### Gate Condition
Coding starts only after sign-off of phases 1-7.

### Stepwise roadmap
1. Freeze scientific spec and threshold table.  
2. Implement/refactor index engines by module contracts.  
3. Add QC pipeline with automated reports.  
4. Build comparison/propagation analytics endpoints.  
5. Implement dashboard panels with validation overlays.  
6. Run reproducibility test suite on full record and event subsets.  
7. Publish v1 scientific methods note and dashboard user guide.

---

## Final Deliverables Checklist

1. Local literature synthesis: complete (Phase 1).  
2. Additional literature findings/gaps: complete (Phase 2).  
3. Feasible drought index set: complete (Phase 3).  
4. Scientific comparison framework: complete (Phase 4).  
5. Quality control plan: complete (Phase 5).  
6. Implementation architecture: complete (Phase 6).  
7. Dashboard design concept: complete (Phase 7).  
8. Implementation roadmap: complete (Phase 8, post-approval execution only).
