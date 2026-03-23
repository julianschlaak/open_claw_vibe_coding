# EGU26 PICO Deck

**Title:** Good runoff ≠ Realistic soil water balance  
**Author:** Julian Schlaak  
**Event:** EGU General Assembly 2026  
**Run:** calibration_mowax_saxony_RE_V2

---

## Final Deck Structure

| # | Slide Title | Key Message |
|---|-------------|-------------|
| 1 | Good runoff ≠ Realistic soil water balance | Title + Research Question |
| 2 | Independent soil moisture reveals hidden internal spread | **Headline figure** (SM spread) |
| 3 | Independent observations constrain internal model behavior | **Map** (Saxony, catchments, CRNS, Tharandt) |
| 4 | Runoff calibration leaves multiple plausible solutions | KGE distribution, top-20 sets |
| 5 | Good runoff fit does not imply good soil moisture | Q-vs-SM scatter (structural) |
| 6 | Soil moisture anomalies reveal process differences | Anomaly-based (process detail) |
| 7 | ET anomalies reveal process differences beyond seasonality | FLUXCOM anomaly comparison |
| 8 | Recharge shows long-term plausibility patterns | BGR climatology |
| 9 | No single parameter set is best across all variables | Simplified scorecard |
| 10 | Summary: Three key findings | + Implication statement |

**Implication:** Runoff-only calibration is insufficient when internal water-balance realism matters.

---

## Backup Slides (14)

- SM: 2018-2020 drought anomalies
- SM: Raw timeseries
- SM: Metrics
- SM: Benchmark comparison
- ET: E_sp summary & heatmap
- ET: Raw monthly (seasonality)
- ET: Anomaly (alternative)
- ET: Benchmark comparison
- Recharge: Alternative view
- Scorecard: Detailed v2
- SM spread: Alternative view
- Workflow
- Concept

---

## Figures Used

Main deck figures (source: calibration_mowax_saxony_RE_V2):
- `pico_s02_main_message_sm_spread_cunnersdorf.png`
- `pico_s03_study_area_reference_map_main.png`
- `pico_s04_runoff_multiple_plausible_solutions.png`
- `pico_s06_q_vs_sm_scatter_all_sets.png`
- `pico_s07d_sm_anomalies_selected_best_sets.png`
- `pico_s07_aet_anomalies_main_revised.png`
- `pico_s08_recharge_long_term_plausibility.png`
- `pico_s09_tradeoff_scorecard_main_simplified.png`

---

## Best Sets

| Set | Role | Description |
|-----|------|-------------|
| set_28 | Runoff-optimal | Best KGE(Q) median |
| set_29 | SM-optimal | Best SM anomaly r |
| set_59 | ET-optimal | Best aET anomaly RMSE |
| set_152 | Recharge-optimal | Best recharge \|Error\| |

**Top-20 rule:** median KGE(Q) across 23 catchments — these are "q_good_sets"

---

## Methodology Notes

- **SM anomaly:** Day-of-year percentile (DOY) — non-parametric, no distributional assumption
- **aET anomaly:** FLUXCOM reference, monthly anomaly
- **E_sp:** Spatial pattern skill (Dembélé et al. 2020), Spearman + CV ratio + RMSE
- **Recharge:** Annual sums, BGR climatology benchmark
- **CRNS:** Cunnersdorf — independent site constraint, area-representative

**Caution:** Reference products are not perfect truth — used for consistency checking.

---

## Usage

Open `index.html` in browser for interactive presentation.

Download `printable.html` for printer-friendly version (all figures embedded).

**Presenter view:** Press `S` in Reveal.js for speaker notes.
