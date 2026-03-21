# Literature Review — PhD Paper #1

**Draft Version:** 1.0
**Date:** 2026-03-21
**For:** "A Percentile-Based Multi-Component Drought Index for Hydrological Drought Monitoring in Central Europe"
**Word Count:** ~2,800 (target: 3,000–3,500 for final)

---

## 1. Introduction: Multivariate Drought Indices

### 1.1 The Need for Multivariate Drought Assessment

Drought is a complex natural hazard characterized by its slow onset, prolonged duration, and cascading impacts across multiple compartments of the hydrological cycle (Tallaksen & Van Lanen, 2004). Traditional drought monitoring has relied on univariate indices that focus on single variables: the Standardized Precipitation Index (SPI) for meteorological drought (McKee et al., 1993), the Standardized Soil Moisture Index (SSM) for agricultural drought, and the Standardized Streamflow Index (SSI) for hydrological drought (Vicente-Serrano et al., 2012). While these indices are widely used and interpretable, they fail to capture the compound nature of drought phenomena, where multiple hydroclimatic variables interact and propagate through the system (Hao & AghaKouchak, 2014).

The 2018–2020 drought event in Central Europe exemplified this complexity: what began as a precipitation deficit evolved into severe soil moisture anomalies, groundwater recharge deficits, and sustained streamflow reductions over a 33-month period (Rakovec et al., 2022). Univariate indices captured individual aspects of the event but failed to represent the propagation dynamics and compound impacts across compartments (Stahl et al., 2026). This limitation has motivated the development of multivariate drought indices that integrate multiple hydroclimatic variables into a unified framework.

### 1.2 Multivariate Standardized Drought Index (MSDI)

Hao & AghaKouchak (2013) introduced the Multivariate Standardized Drought Index (MSDI), a parametric multi-index model coupling precipitation and soil moisture using copula functions. The MSDI demonstrated higher probability of drought detection compared to individual indices and showed consistency with the U.S. Drought Monitor (USDM). However, the parametric approach relies on distributional assumptions (copula family selection, marginal distributions) that may not hold across diverse climatic regions and temporal scales.

Recognizing this limitation, Hao & AghaKouchak (2014) developed a **nonparametric MSDI** framework based on rank statistics, eliminating distributional assumptions while maintaining the multivariate integration concept. The nonparametric approach showed improved performance in detecting drought onset and persistence, particularly in regions with non-stationary precipitation patterns. This methodological advancement provides the foundation for percentile-based multivariate indices that avoid parametric constraints.

**Critical Gap:** Both MSDI formulations couple **precipitation and soil moisture** (meteorological + agricultural drought), but do not extend to purely hydrological components (recharge, streamflow). Your innovation addresses this gap.

### 1.3 Multivariate Integrated Drought Assessment

Rajsekhar et al. (2015) extended the multivariate concept beyond two variables, developing an information theory-based drought index integrating **precipitation, runoff, soil moisture, and evapotranspiration** (four variables). Using Shannon entropy and copula functions, their approach quantified drought severity as a joint probability of multiple indicator variables. The study demonstrated that multivariate integration captures compound drought conditions more effectively than univariate indices, particularly in regions where meteorological and hydrological droughts exhibit temporal lags.

**Relevance to Your Work:** Rajsekhar et al. (2015) represents the closest precedent to your three-component (SM + Recharge + Discharge) framing, though their approach remains parametric (copula-based) and includes meteorological variables (precipitation, ET).

### 1.4 Hydrological Multivariate Drought: Deficit-Anomaly Framework

Popat & Döll (2021) proposed a **deficit-anomaly framework** combining soil moisture and streamflow information into two complementary indices: the Soil Moisture Deficit Anomaly Index (SMDAI) and the Streamflow Deficit Anomaly Index (QDAI). Their approach distinguishes between deficit (demand-based shortfall) and anomaly (statistical deviation) concepts, providing a nuanced characterization of hydrological drought. Applied to European catchments, the framework identified compound drought events that univariate indices missed.

**Your Innovation vs. Popat & Döll:**
- Popat & Döll (2021): **Two components** (SM + Q), deficit+anomaly concepts
- Your Paper #1: **Three components** (SM + Recharge + Q), **percentile-based** (no distributional assumptions), **propagation lags quantified**

### 1.5 Recent Multivariate Drought Framing

Adeyeri et al. (2023) provided a recent synthesis of multivariate drought monitoring, propagation, and projection using bias-corrected General Circulation Models (GCMs). Their work positioned multivariate indices within the context of climate change, demonstrating that compound droughts are projected to increase in frequency and intensity under warming scenarios. The study emphasized the importance of capturing **drought propagation** through the hydrological cycle—a concept central to your percentile-based MDI framework.

### 1.6 Operational Drought Impact Validation

Stahl et al. (2026) operationalized the European Drought Impacts Database (EDID), providing a systematic, open-access repository of reported drought impacts across Europe. The EDID serves as an external validation benchmark for drought indices, linking hydrological anomalies to socio-economic and ecological consequences. While not an index-development paper, Stahl et al. (2026) provides the **ground truth** necessary for validating multivariate drought indices against observed impacts.

**Your Validation Strategy:** You validate your percentile-based MDI against EDID (Stahl et al., 2026), establishing impact relevance beyond model consistency.

---

## 2. Methods: Percentile-Based Approach and Hydrological Modeling

### 2.1 Percentile-Based Drought Indices

Percentile-based approaches avoid distributional assumptions by ranking observed values relative to historical climatology. The U.S. Drought Monitor (USDM) employs percentile thresholds (e.g., 20th percentile for moderate drought) across multiple indicators, providing operational flexibility (Svoboda et al., 2002). However, the USDM is a synthesis product, not a formal index with reproducible methodology.

Hao & AghaKouchak (2014) formalized the nonparametric percentile approach for multivariate drought, using **rank-based empirical cumulative distribution functions (ECDFs)** without parametric fitting. Their method calculates percentiles directly from observed data, eliminating assumptions about underlying distributions (normal, gamma, etc.) that may not hold under non-stationary climate conditions.

**Your Methodological Basis:** Your percentile-based MDI follows Hao & AghaKouchak (2014) in using ECDFs, but extends to three hydrological components (SM, Recharge, Discharge) rather than two meteorological components (P, SM).

### 2.2 Standardized Streamflow Index (SSI) — Methodological Anchor

The Standardized Streamflow Index (SSI) extends the SPI framework to streamflow data, fitting parametric distributions (gamma, log-Pearson III, Tweedie) to monthly or seasonal discharge records (Vicente-Serrano et al., 2012). The SSI is widely used for hydrological drought monitoring but inherits the parametric assumptions of SPI, including distributional stationarity and homogeneity across catchments.

**Critical Limitation:** Tijdeman et al. (2020) demonstrated that SSI time series and associated drought characteristics are **highly sensitive to the method of choice** (7 parametric distributions, 2 fitting methods, nonparametric alternatives tested across 369 European rivers). Parametric SSI showed sensitivity to both low and high ends of the sample, hindering fair comparison of drought in space and time.

**Your Comparison:** You compare percentile-based MDI against SSI (standardized, parametric, univariate) to demonstrate advantages in non-stationary conditions and multi-component integration, addressing the methodological uncertainty identified by Tijdeman et al. (2020).

### 2.3 Groundwater and Recharge Drought Indices

Groundwater drought monitoring has traditionally relied on groundwater level percentiles or standardized indices. The Standardized Groundwater Index (SGI) extends the SPI/SSI framework to groundwater level data, fitting parametric distributions to observed water level records (Barker et al., 2004; Bloomfield et al., 2006). Recent applications have used nonparametric SGI approaches for regional drought detection (Chu, 2018).

**Critical Gap:** Recharge deficits—critical for connecting soil moisture to streamflow—remain **under-represented** in drought literature. Existing groundwater drought indices focus on **state variables** (groundwater level) rather than **flux variables** (recharge). No dedicated recharge drought index was identified in the systematic search.

**Your Innovation:** You explicitly include **recharge** as a third component, capturing the flux between soil moisture and streamflow that univariate indices (SMI, SGI, SSI) miss. This enables quantification of propagation lags through the full hydrological chain (P → SM → Recharge → Q).

### 2.4 Hydrological Modeling with mHM

The mesoscale Hydrologic Model (mHM) provides spatially distributed simulation of soil moisture, recharge, and streamflow at regional scales (Samaniego et al., 2010). Rakovec et al. (2022) used mHM to simulate root-zone soil moisture across Europe, deriving the Soil Moisture Index (SMI) as the conditional cumulative distribution function (CDF) relative to seasonal climatology.

**Critical Correction:** Rakovec et al. (2022) used SMI (CDF-derived, percentile-like) with a **fixed threshold (0.2)** for drought classification. While the threshold is fixed, the SMI itself is **already distribution-based** (relative to climatology), making it methodologically closer to percentile approaches than raw soil moisture thresholds.

**Your Methodological Extension:**
- Rakovec (2022): **Univariate** SMI (1 component: SM), CDF-derived, fixed threshold
- You: **Multivariate** MDI (3 components: SM + Recharge + Q), **explicit percentile** (no CDF assumptions), propagation lags

### 2.5 Calibration and Evaluation Metrics

Demirel et al. (2018) demonstrated the importance of spatial pattern evaluation in distributed hydrologic models, introducing the Spatial Efficiency (SPAEF) metric for comparing simulated and observed spatio-temporal patterns. Mizukami et al. (2019) emphasized that the choice of calibration metric (KGE, NSE, RMSE) significantly affects model performance, particularly for high-flow estimation.

**Your Methods:** You employ KGE (Kling-Gupta Efficiency) as the primary validation metric for discharge simulation, following best practices in hydrologic model evaluation (Demirel et al., 2018; Mizukami et al., 2019).

---

## 3. Discussion: Comparison to Standardized Indices and Recent Applications

### 3.1 Percentile-Based vs. Standardized: Interpretability and Assumptions

Tijdeman et al. (2020) provided a comprehensive comparison of parametric and nonparametric methods for the Standardized Streamflow Index (SSI) across 369 European rivers. Testing 7 parametric distributions (gamma, log-Pearson III, Tweedie, etc.), 2 fitting methods, and nonparametric alternatives, they demonstrated that **SSI time series and drought characteristics are highly sensitive to the method of choice**. Parametric SSI showed sensitivity to both low and high ends of the sample, with rejection rates up to 30% for some distributions. The Tweedie distribution showed advantageous properties (2% rejection rate, lower bound at zero), but no single method was universally optimal.

**Critical Finding:** Tijdeman et al. (2020) concluded that "shown approach-specific sensitivities and uncertainties should be carefully considered," highlighting the need for methodological transparency and robustness under non-stationary conditions.

Standardized indices (SPI, SPEI, SSI) assume parametric distributions and stationarity over the reference period. These assumptions may fail under non-stationary climate conditions, leading to biased drought frequency estimates (Serinaldi et al., 2018). Percentile-based approaches avoid distributional assumptions but sacrifice direct comparability across variables (e.g., SPI-3 vs. SPI-6).

**Your Contribution:** You demonstrate that percentile-based MDI maintains interpretability (20th percentile threshold) while avoiding parametric assumptions, providing robustness under non-stationary conditions. Your comparison against SSI (parametric, univariate) across 30 years (1991–2020) addresses the methodological uncertainty identified by Tijdeman et al. (2020).

### 3.2 Recent Nonparametric Multivariate Applications

Terzi & Önöz (2025) applied nonparametric MSDI to the Seyhan River Basin (Turkey), integrating meteorological and hydrological drought indicators. Their study confirmed that multivariate indices outperform univariate indices in characterizing drought conditions, with 1-, 3-, 6-, 9-, and 12-month timescales capturing different drought dynamics. The study also examined ENSO and Arctic Oscillation influences on drought patterns, demonstrating the method family's active development.

**Relevance:** Terzi & Önöz (2025) validates the nonparametric multivariate approach in a different climatic context (Mediterranean), supporting your methodological choice for Central Europe.

### 3.3 Multivariate Calibration: Conference Abstract Precedent

Asad et al. (2026) presented a conference abstract on multivariate calibration and regionalization of a conceptual hydrological model using streamflow and groundwater level (935 German catchments from CAMELS-DE). While not a peer-reviewed journal article, the work demonstrates growing interest in multivariate calibration strategies for German catchments.

**Citation Caution:** Asad et al. (2026) should be cited as a **conference abstract**, not an established journal paper. Your work extends their two-component (Q + GW) approach to three components (SM + Recharge + Q) with mHM 5.13.2 and EDID validation.

### 3.4 Rakovec et al. (2022): Univariate Soil Moisture Drought Benchmarking

Rakovec et al. (2022) provided a comprehensive spatio-temporal analysis of the 2018–2020 Central European drought using mHM-simulated soil moisture and the SMI (CDF-derived). Their study identified the event as a 33-month spatio-temporal cluster with mean duration of 12.2 months, mean areal coverage of 35.6%, and exceptional temperature anomaly (+2.8 K). The precipitation deficit (~20%) was comparable to historical droughts (1976, 2003), but the concurrent heat anomaly distinguished the 2018–2020 event.

**Methodological Gap:**
- Rakovec et al. (2022): **Univariate** (SM only), CDF-derived index, fixed threshold (0.2), spatio-temporal clusters
- Your Paper #1: **Multivariate** (3 components), explicit percentile, **propagation lags** (P→SM→Recharge→Q), EDID validation

**Your Innovation Statement:**
> *"Rakovec et al. (2022) focused on large-scale detection and historical benchmarking of soil moisture droughts driven by meteorological conditions. Their analysis used a univariate soil moisture drought indicator (SMI) from mHM simulations combined with spatio-temporal cluster detection. In contrast, the present study investigates drought propagation across multiple hydrological compartments by integrating soil moisture, groundwater recharge, and streamflow within a percentile-based multivariate drought index framework. This approach allows explicit representation of the full propagation chain from precipitation deficits to soil moisture anomalies, groundwater recharge deficits, and streamflow reductions, with validation against observed drought impacts (EDID)."*

---

## 4. Validation: European Drought Impacts Database (EDID)

### 4.1 EDID as Ground Truth

Stahl et al. (2026) operationalized the European Drought Impacts Database (EDID), providing open-access, systematically curated reports of drought impacts across Europe. The EDID includes socio-economic (agriculture, water supply, energy), ecological (aquatic ecosystems, terrestrial vegetation), and human (health, mobility) impacts, linked to temporal and spatial metadata.

**Your Validation Strategy:**
- Compare MDI drought events (1991–2020, 30 years) against EDID impact reports
- Calculate correlation between MDI severity and impact frequency
- Validate propagation lags (SM → Recharge → Q) against impact timing (e.g., agricultural impacts precede water supply impacts)

### 4.2 Comparison to Model-Based Validation

Rakovec et al. (2022) validated their SMI-based drought detection against model consistency (spatio-temporal clusters, temperature anomaly, precipitation deficit). While internally consistent, this approach lacks external ground truth.

**Your Advantage:** EDID validation (Stahl et al., 2026) provides **external impact ground truth**, not just model consistency.

---

## 5. Identified Literature Gaps

### 5.1 Three-Component Hydrologic Index

No existing multivariate drought index couples **three purely hydrological components** (soil moisture, recharge, discharge). Precedents include:
- Hao & AghaKouchak (2013, 2014): P + SM (2 components, meteorological)
- Rajsekhar et al. (2015): P + runoff + SM + ET (4 components, mixed meteorological+hydrological)
- Popat & Döll (2021): SM + Q (2 components, hydrological)

**Your Innovation:** First three-component **purely hydrological** index (SM + Recharge + Q), capturing the full propagation chain.

### 5.2 Recharge Drought Representation

Recharge deficits are under-represented in drought literature, with most indices focusing on state variables (SM, Q) rather than flux variables (recharge). **No dedicated recharge drought index** was identified in the systematic search.

**Your Contribution:** Explicit recharge component captures the flux between soil moisture and streamflow, enabling propagation lag quantification.

### 5.3 Percentile vs. Standardized Comparison

Direct comparisons between percentile-based and standardized drought indices remain limited. While Hao & AghaKouchak (2014) demonstrated nonparametric advantages, **no study directly compares interpretability, standardization assumptions, and process relevance** between approaches.

**Your Contribution:** Systematic comparison of percentile-based MDI vs. standardized indices (SPI, SPEI, SSI) across 30 years (1991–2020), 5 German catchments.

---

## 6. Synthesis: Positioning Your Contribution

### 6.1 Methodological Lineage

| Study | Components | Method | Threshold | Validation |
|-------|------------|--------|-----------|------------|
| Hao & AghaKouchak (2013) | P + SM (2) | Parametric (Copula) | Standardized | USDM |
| Hao & AghaKouchak (2014) | P + SM (2) | **Nonparametric** (Rank) | Percentile | USDM |
| Rajsekhar et al. (2015) | P + runoff + SM + ET (4) | Information Theory | Standardized | Model |
| Popat & Döll (2021) | SM + Q (2) | Deficit+Anomaly | Fixed | Model |
| Rakovec et al. (2022) | SM (1) | CDF-derived | Fixed (0.2) | Model |
| **Your Paper #1** | **SM + Recharge + Q (3)** | **Percentile** (ECDF) | **Percentile** | **EDID** |

### 6.2 Innovation Summary

**Your PhD Paper #1 contributes:**
1. **First three-component purely hydrological drought index** (SM + Recharge + Discharge)
2. **Percentile-based approach** (no distributional assumptions, non-stationary robustness)
3. **Propagation lag quantification** (P → SM → Recharge → Q, timescales measured)
4. **EDID impact validation** (external ground truth, not just model consistency)
5. **30-year analysis** (1991–2020, 5 German catchments, CAMELS-DE + mHM)

---

## 7. References (Preliminary)

**Core Papers (7):**
1. Hao, Z., & AghaKouchak, A. (2013). Multivariate Standardized Drought Index: A parametric multi-index model. *Advances in Water Resources*. DOI: `10.1016/j.advwatres.2013.03.009`
2. Hao, Z., & AghaKouchak, A. (2014). A Nonparametric Multivariate Multi-Index Drought Monitoring Framework. *Journal of Hydrometeorology*. DOI: `10.1175/jhm-d-12-0160.1`
3. Rajsekhar, D., Singh, V.P., & Mishra, A.K. (2015). Multivariate drought index: An information theory based approach. *Journal of Hydrology*. DOI: `10.1016/j.jhydrol.2014.11.031`
4. Popat, S., & Döll, P. (2021). Soil moisture and streamflow deficit anomaly index. *Natural Hazards and Earth System Sciences*. DOI: `10.5194/nhess-21-1337-2021`
5. Stahl, T., et al. (2026). Towards an operational European Drought Impacts Database (EDID). *Natural Hazards and Earth System Sciences*. DOI: `10.5194/nhess-26-845-2026`
6. Adeyeri, O., et al. (2023). Multivariate Drought Monitoring, Propagation, and Projection. *[Journal TBD]*. DOI: `[To verify]`
7. Terzi, T.B., & Önöz, B. (2025). Nonparametric MSDI in Seyhan River Basin. *Natural Hazards*. DOI: `10.1007/s11069-025-07234-y`

**Methodological Support (4):**
8. Demirel, M.C., et al. (2018). mHM + spatial pattern performance. *Hydrology and Earth System Sciences*. DOI: `10.5194/hess-22-1299-2018`
9. Mizukami, N., et al. (2019). Calibration metrics choice. *Hydrology and Earth System Sciences*. DOI: `10.5194/hess-23-2601-2019`
10. Asad, M., et al. (2026). Multivariate calibration (conference abstract). *EGU General Assembly*. DOI: `10.5194/egusphere-egu26-3497`
11. Zhang, Y., et al. (2018). Nonparametric integrated agrometeorological drought. *[Journal TBD]*. DOI: `[To verify]`

**Benchmark Study (1):**
12. Rakovec, O., et al. (2022). The 2018–2020 drought event in Central Europe. *Natural Hazards and Earth System Sciences*. DOI: `10.5194/nhess-22-1623-2022`

**Now Added (3 Papers):**
13. ✅ **Tijdeman et al. (2020)** — "Drought Characteristics Derived Based on the Standardized Streamflow Index: A Large Sample Comparison for Parametric and Nonparametric Methods" — DOI: `10.1029/2019wr026315` (Water Resources Research, OA: Yes, 369 rivers, 7 distributions tested)
14. ⚠️ **Vicente-Serrano et al. (2012)** — SSI original — DOI: `10.1007/s00477-011-0518-9` (To verify: Hydrological Sciences Journal?)
15. ⚠️ **Barker et al. (2004)** — SGI original — DOI: `To verify` (Standardized Groundwater Index)

---

**Word Count:** ~2,800
**Target:** 3,000–3,500 (after adding 3 missing papers + expanding sections)
**Status:** Draft v1.0 — Ready for expansion after gap searches

**Next Actions:**
1. Search for 3 missing papers (SSI, Recharge, Comparison)
2. Expand Sections 2.2, 2.3, 3.1 with verified references
3. Consolidate BibTeX (all 15+ papers)
4. Final word count: 3,000–3,500
