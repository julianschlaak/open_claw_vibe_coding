# A Matrix Drought Index Approach for Integrated Hydrological Drought Assessment: A 30-Year mHM Simulation Study

## Abstract

Hydrological drought assessment is often conducted with single-compartment indicators that isolate either soil moisture, recharge, or streamflow deficits. While such indicators are useful for monitoring, they can miss coupled process behavior and temporal propagation effects across compartments. This study presents an integrated matrix drought framework based on long-term simulation outputs from the mesoscale Hydrologic Model (mHM, version 5.13.2) for catchment 90410700 over the period 1991-2020. We combine percentile-based soil moisture diagnostics, recharge anomalies, and discharge deficits in a weighted Matrix Drought Index (MDI), and we explicitly evaluate time-lag relationships between meteorological forcing, vadose-zone storage response, groundwater recharge, and routed streamflow.

The methodological workflow consists of two complementary components: (i) a standard drought pipeline generating temporal and seasonal diagnostics, drought duration statistics, and observed-versus-simulated discharge validation metrics; and (ii) an advanced pipeline estimating lag-correlation structures and constructing a multi-variable drought severity index using a weighted combination of soil moisture, recharge, and discharge (40/30/30). We further report model skill using Kling-Gupta efficiency (KGE), correlation coefficient, root mean square error (RMSE), mean absolute error (MAE), and Nash-Sutcliffe efficiency (NSE).

Results demonstrate that integrated drought characterization improves interpretability of event onset, persistence, and recovery compared with single-variable views. The lag analysis reveals non-zero delay structures between compartments, supporting process-based interpretation of drought propagation. The MDI captures compound dry states where individual indicators alone remain ambiguous. Discharge validation confirms realistic hydrograph dynamics for the examined setup and supports the utility of the simulation outputs for drought diagnostics. Despite uncertainties linked to stationarity assumptions and threshold sensitivity, the proposed framework is practical for operational drought screening, scenario evaluation, and comparative basin studies. The approach is fully scriptable and reproducible through a queue-based OpenClaw-Codex bridge architecture.

## 1. Introduction

Drought is a multi-faceted hazard with substantial impacts on ecosystems, agriculture, water supply systems, hydropower generation, and riverine habitats. In contrast to flood hazards, drought develops slowly, often with delayed effects and nonlinear feedbacks between atmosphere, soil, groundwater, and river networks. This gradual evolution makes drought detection challenging: early signals may appear in one compartment while others respond later or with attenuated magnitude.

Hydrological drought research has produced a broad set of indicators, including meteorological, agricultural, and hydrological indices. For hydrological applications, streamflow-based indicators are common because discharge is directly observable at gauges and relevant for management. However, discharge alone cannot fully describe storage dynamics in the unsaturated zone or recharge conditions in deeper layers. Soil moisture and recharge metrics add physical context but often remain disconnected in routine workflows.

A key limitation of many index-based applications is compartment isolation. Soil moisture anomalies may suggest severe conditions while streamflow appears near normal due to routing memory or groundwater buffering. Conversely, streamflow deficits can persist after shallow soils have partially recovered. Such mismatches are not necessarily model errors; they often represent real process lags. If these lags are not analyzed explicitly, interpretation of drought onset and termination becomes ambiguous.

To address this gap, integrated drought frameworks are needed. These frameworks should maintain physical interpretability, remain computationally feasible for operational use, and allow transparent validation against observed quantities. In this study, we propose a Matrix Drought Index (MDI) that combines three hydrologically relevant components: soil moisture state, recharge condition, and streamflow anomaly. The index is accompanied by lag-correlation analysis to quantify temporal propagation among compartments.

The computational basis is the mesoscale Hydrologic Model (mHM), a well-established multi-scale modeling framework designed for process-based hydrological simulation and regional transferability. We use mHM version 5.13.2 in a reproducible containerized environment and analyze a 30-year simulation window (1991-2020) for catchment 90410700. The workflow has been implemented as modular pipelines that generate publication-ready figures and tabular outputs.

The objectives of this study are therefore fourfold:

1. Derive standardized and percentile-based drought diagnostics from long-term mHM outputs.
2. Quantify lag relationships between core hydro-climatic response variables.
3. Develop and evaluate a weighted Matrix Drought Index integrating multiple compartments.
4. Provide an operationally robust and reproducible automation architecture for end-to-end analysis.

By combining conventional diagnostics with lag-aware integration, we aim to improve drought interpretation under multi-compartment dynamics and to support transfer to additional basins with minimal workflow changes.

## 2. Study Area and Data

The study focuses on catchment `90410700` represented in the project as `catchment_custom`. The catchment setup includes topographic, land-surface, soil, and meteorological forcing inputs prepared for mHM. While detailed physiographic descriptors are maintained in model input files, the analysis here emphasizes methodological reproducibility and long-term drought dynamics.

The primary simulation period considered for interpretation is 1991-2020. Model setup and runtime controls are defined through mHM namelists (`mhm.nml`, `mhm_parameter.nml`, `mhm_outputs.nml`). A warm-up period is included to reduce sensitivity to initial conditions, ensuring physically meaningful storage states before evaluation years.

Input data categories include:

- precipitation forcing
- temperature forcing
- potential evapotranspiration
- terrain and river network descriptors
- land cover and LAI class maps
- soil and geology class definitions

Model outputs used in this analysis include both gridded and routed diagnostics:

- soil moisture and flux states (`mHM_Fluxes_States.nc`)
- routed discharge (`mRM_Fluxes_States.nc`)
- discharge outputs (`discharge.nc`, `daily_discharge.out`)

Observed and simulated discharge series are used jointly for validation diagnostics. The text-based discharge file supports explicit extraction of paired `Qobs` and `Qsim` columns for metric computation and visual comparison.

## 3. Methods

### 3.1 Soil Moisture Index (SMI)

SMI is derived as a percentile-based representation of relative soil moisture state. To avoid strong seasonal bias, daily values are mapped to season-aware empirical distributions where relevant. This prevents the artificial interpretation that summer is always dry and winter always wet purely due to climatological seasonality.

For operational diagnostics, the workflow can use layer-specific soil water content variables and convert to volumetric scale based on effective depth assumptions. In current quick-fix mode, top-layer content (`SWC_L01`) is scaled by selected layer depth for robust comparability and bounded values.

### 3.2 Standardized Soil Moisture Index (SSI)

SSI-like diagnostics are obtained by fitting probability distributions to soil moisture series and transforming probabilities to standardized normal space. The standardized transformation enables cross-time comparability and threshold-based interpretation (e.g., moderate, severe, extreme drought classes).

### 3.3 Streamflow Drought Index (SDI)

SDI diagnostics are based on discharge anomalies, including low-percentile deficits and standardized transformations over selected aggregation windows. Streamflow deficits provide direct management relevance but reflect integrated upstream and subsurface memory effects.

### 3.4 Matrix Drought Index (MDI)

We propose a weighted index that combines normalized soil moisture, recharge, and discharge drought signals:

- Soil moisture contribution: 40%
- Recharge contribution: 30%
- Discharge contribution: 30%

The weights prioritize near-surface state response while preserving hydrological flux and routing relevance. The resulting index is classified into discrete drought classes for clear interpretation and map/plot compatibility.

### 3.5 Lag-Correlation Analysis

Lag-correlation analysis is used to identify response delays among variables. For each variable pair, correlations are evaluated across positive and negative lags, and optimal lag is identified by maximum absolute correlation under plausibility constraints.

This allows explicit quantification of drought propagation, e.g.:

- forcing to soil moisture response
- soil moisture to recharge response
- recharge to streamflow response

### 3.6 Performance Metrics

Discharge validation uses:

- Kling-Gupta Efficiency (KGE)
- Pearson correlation coefficient (r)
- Root Mean Square Error (RMSE)
- Mean Absolute Error (MAE)
- Nash-Sutcliffe Efficiency (NSE)
- bias ratio (beta)

Metrics are displayed directly on validation figures to ensure immediate interpretability of model realism and uncertainty context.

## 4. Results

### 4.1 Temporal dynamics

The time-series diagnostics reveal alternating dry and recovery phases over the 30-year window. Multi-variable comparison indicates that soil moisture and recharge often react earlier than discharge, especially during onset periods. Prolonged deficits are better captured when combining variables rather than relying on a single curve.

### 4.2 Spatial-temporal patterns

Heatmaps for soil moisture, recharge, and discharge percentiles highlight recurring seasonal structures and interannual variability. Extreme dry years present coherent low-percentile signatures across compartments, while moderate events can remain compartment-specific.

### 4.3 Lag analysis

Lag-correlation plots show non-zero optimal lags, supporting delayed propagation between storages and runoff response. This confirms that synchronous thresholding across variables may miss process timing and should be complemented by lag-aware interpretation.

### 4.4 Matrix index evaluation

The MDI captures compound drought states with clearer event separation than individual indices. Class transitions in the matrix representation correspond to prolonged low-flow conditions and recharge deficits, improving event narrative consistency.

### 4.5 Validation against observed discharge

Observed-versus-simulated hydrographs show consistent co-variability in major fluctuations. Performance metrics indicate acceptable model skill for drought-oriented interpretation, though uncertainty remains for peak and tail behavior. Embedding metrics within the figure improves transparency and rapid quality checks.

## 5. Discussion

The integrated matrix approach addresses a recurring challenge in hydrological drought analysis: compartment mismatch through time. Traditional single-indicator workflows are straightforward but can overstate or understate drought severity when storage and flux responses are asynchronous. By combining variables and preserving lag information, the proposed framework improves process consistency.

Compared with existing literature on mHM-based drought diagnostics, the present approach contributes operational modularity and explicit bridge-based automation. The queue-worker architecture is particularly relevant in environments where interactive tooling is unstable or partially available. Instead of depending on ad-hoc command execution, serialized jobs with retries improve reliability and auditability.

Several limitations should be acknowledged. First, percentile and standardized methods assume quasi-stationary reference behavior over the analysis period. Under strong long-term trends, this can bias drought class frequency. Second, weighting in the matrix index is expert-driven and may require calibration or sensitivity testing across climates. Third, layer-depth assumptions in volumetric conversion can affect absolute values and threshold interpretation.

Despite these constraints, transfer potential is strong. The framework is domain-parameterized and can be adapted to additional catchments with consistent folder conventions, updated namelists, and standardized output extraction. Future work should include uncertainty propagation, climate scenario stress testing, and objective optimization of matrix weights and lag windows.

## 6. Conclusions

This study presents a reproducible drought analysis framework integrating mHM simulation outputs, lag-correlation diagnostics, and a weighted Matrix Drought Index. Applied to a 30-year simulation for catchment 90410700, the workflow demonstrates the value of multi-compartment interpretation for identifying drought onset, persistence, and recovery.

Key conclusions are:

1. Integrated diagnostics reduce ambiguity relative to single-variable drought interpretation.
2. Lag-aware analysis is essential for physically meaningful propagation assessment.
3. Matrix-based classification improves detection of compound drought states.
4. Inline validation metrics for Qobs/Qsim enhance transparency of model-based inference.
5. The OpenClaw-Codex bridge enables robust automation under unstable interactive conditions.

The framework is ready for extension to additional domains and for refinement toward publication-quality comparative studies.

## Acknowledgements

We acknowledge the mHM development community for providing a robust hydrological modeling foundation and all contributors who supported data preparation, workflow engineering, and operational validation.

## References

- Samaniego, L., and Kumar, R. mHM model development and multiscale parameter regionalization publications.
- Kumar, R., et al. Regionalized hydrological modeling and process transferability studies.
- Rakovec, O., et al. Hydrological model diagnostics, benchmarking, and uncertainty-focused studies.
- Foundational literature on SMI, SSI, and SDI methodologies.
- Recent hydrological drought integration and propagation analysis papers.

## Figure Captions

**Figure 1.** Temporal drought dynamics for the target catchment using percentile and standardized indicators (`analysis/plots/catchment_custom/01_drought_timeseries.png`).

**Figure 2.** Soil moisture percentile heatmap highlighting seasonal and interannual drought structure (`analysis/plots/catchment_custom/02_heatmap_smi.png`).

**Figure 3.** Recharge percentile heatmap showing groundwater renewal deficits (`analysis/plots/catchment_custom/03_heatmap_recharge.png`).

**Figure 4.** Discharge percentile heatmap for low-flow drought characterization (`analysis/plots/catchment_custom/04_heatmap_discharge.png`).

**Figure 5.** Lag-correlation analysis identifying optimal delays between hydrological compartments (`analysis/plots/catchment_custom/09_lag_correlation.png`).

**Figure 6.** Matrix Drought Index classification and component behavior (`analysis/plots/catchment_custom/10_matrix_drought_index.png`).

**Figure 7.** Observed versus simulated discharge with embedded skill metrics (`analysis/plots/catchment_custom/05_discharge_analysis.png`).
