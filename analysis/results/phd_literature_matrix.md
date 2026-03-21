# PhD-Ready Literature Verification Matrix

**Paper:** Percentile-based Multivariate Drought Index (MDI) — SM + Recharge + Discharge vs. Standardized Indices (SPI, SPEI, SSI)
**Date:** 2026-03-21
**Status:** Verified via external LLM (Perplexity / publisher pages / DOI resolvers)

---

## 📊 Verification Matrix

| # | Paper | DOI | Exact Contribution | Direct Relevance to Your Index | Verdict | Citation Use |
|---|-------|-----|-------------------|-------------------------------|---------|--------------|
| **1** | Hao & AghaKouchak (2013) | `10.1016/j.advwatres.2013.03.009` | Parametric MSDI (Copula-based, P+SM) | ⚠️ Partial (meteorological, 2 components, parametric) | ✅ KEEP | **Introduction** (MSDI origin), **Discussion** (parametric vs. nonparametric) |
| **2** | Hao & AghaKouchak (2014) | `10.1175/jhm-d-12-0160.1` | Nonparametric MSDI (rank-based, P+SM, vs. USDM) | ✅ High (nonparametric method basis, but still P+SM) | ✅ KEEP | **Introduction** (nonparametric justification), **Methods** (rank-based approach) |
| **3** | Rajsekhar et al. (2015) | `10.1016/j.jhydrol.2014.11.031` | Multivariate drought index (information theory, P+runoff+SM+ET = 4 variables) | ✅✅ Very High (closest to your 3-component framing, multivariate integrated) | ✅ KEEP | **Introduction** (multivariate precedent), **Discussion** (multi-variable integration) |
| **4** | Popat & Döll (2021) | `10.5194/nhess-21-1337-2021` | Deficit Anomaly Index (SMDAI+QDAI, SM+Q, deficit+anomaly concepts) | ✅✅ Very High (hydrological, 2 components, deficit+anomaly framework) | ✅ KEEP | **Introduction** (hydrological multivariate), **Discussion** (deficit+anomaly vs. percentile) |
| **5** | Stahl et al. (2026) | `10.5194/nhess-26-845-2026` | EDID operational database (impact reporting, validation benchmark) | ✅ High (validation, NOT index development) | ✅ KEEP | **Validation** (EDID ground truth), **Discussion** (impact comparison) |
| **6** | Demirel et al. (2018) | `10.5194/hess-22-1299-2018` | mHM + spatial pattern calibration (SPAEF, AET from MODIS) | ⚠️ Medium (methodological support, NOT drought index) | ⚠️ CONDITIONAL | **Methods** (mHM justification, spatial evaluation) — omit if not discussing calibration |
| **7** | Mizukami et al. (2019) | `10.5194/hess-23-2601-2019` | Calibration metrics (objective function choice, high-flow estimation) | ⚠️ Medium (methodological support, NOT drought index) | ⚠️ CONDITIONAL | **Methods** (calibration strategy) — omit if not discussing metrics |
| **8** | Asad et al. (2026) | `10.5194/egusphere-egu26-3497` | Multivariate calibration (streamflow+groundwater, CAMELS-DE, conceptual model) | ⚠️ Medium (methodologically adjacent, conference abstract) | ⚠️ CAUTION | **Discussion** (multivariate calibration precedent) — cite as abstract, not journal |
| **9** | Adeyeri et al. (2023) | To verify | Multivariate drought monitoring, propagation, projection (GCM bias-corrected) | ✅ High (recent framing, propagation literature) | ✅ ADD | **Introduction** (recent multivariate framing), **Discussion** (propagation context) |
| **10** | Zhang et al. (2018) | To verify | Nonparametric integrated agrometeorological drought monitoring | ✅ Medium (nonparametric extension beyond P+SM) | ✅ ADD | **Methods** (nonparametric precedent), **Discussion** (process-integrated combinations) |
| **11** | Terzi & Önöz (2025) | `10.1007/s11069-025-07234-y` | Nonparametric MSDI application (Seyhan River Basin, meteorological+hydrological) | ✅ Medium (application-oriented, shows method family active) | ✅ ADD | **Discussion** (recent nonparametric application, 2025) |
| **12** | SSI Reference Paper | NOT IDENTIFIED | Standardized Streamflow Index methodology (original / Vicente-Serrano) | ❌ Missing (your comparison includes SSI, no anchor paper) | 🔴 ADD | **Methods** (SSI definition), **Comparison** (SSI vs. MDI) |
| **13** | Recharge/Groundwater Drought | NOT IDENTIFIED | Groundwater drought index, recharge deficit/anomaly | ❌ Missing (your 3 components: SM✅, Q✅, Recharge❌) | 🔴 ADD | **Methods** (recharge drought definition), **Discussion** (groundwater component) |
| **14** | Percentile vs. Standardized Comparison | NOT IDENTIFIED | Direct comparison: percentile-based vs. standardized indices (interpretability, assumptions) | ❌ Missing (your core claim: percentile-based advantage) | 🔴 ADD | **Discussion** (interpretability, standardization assumptions, gains/losses) |

---

## 🎯 Final Verdict Summary

### ✅ KEEP (Core Papers — 5)

| Paper | Why Keep |
|-------|----------|
| Hao (2013) | Foundational (MSDI origin, parametric) |
| Hao (2014) | **Nonparametric basis** (methodologically closer to your approach) |
| Rajsekhar (2015) | **Multivariate (4 variables)** — closest to your 3-component framing |
| Popat & Döll (2021) | **Hydrological multivariate** (SM+Q, deficit+anomaly) |
| Stahl (2026) | **Validation** (EDID impact benchmark) |

### ✅ ADD (New Core Papers — 3)

| Paper | Why Add |
|-------|---------|
| Adeyeri (2023) | Recent multivariate framing (propagation, projection) |
| Zhang (2018) | Nonparametric integrated monitoring (process-integrated) |
| Terzi (2025) | Recent nonparametric application (method family active) |

### ⚠️ CONDITIONAL (Methodological Support — 3)

| Paper | Use If | Omit If |
|-------|--------|---------|
| Demirel (2018) | Discussing mHM calibration / spatial evaluation | Not discussing calibration methods |
| Mizukami (2019) | Discussing objective functions / metric sensitivity | Not discussing calibration strategy |
| Asad (2026) | Discussing multivariate calibration precedent | Prefer journal papers only (cite cautiously as abstract) |

### 🔴 CRITICAL MISSING (Must Add — 3)

| Gap | What to Search | Why Critical |
|-----|----------------|--------------|
| **SSI Reference** | "Vicente-Serrano SSI original", "Standardized Streamflow Index methodology" | Your comparison includes SSI — need anchor paper |
| **Recharge/Groundwater Drought** | "groundwater drought index percentile", "recharge drought monitoring" | Your 3 components: SM✅, Q✅, Recharge❌ |
| **Percentile vs. Standardized** | "percentile-based vs standardized drought index comparison", "nonparametric vs parametric drought" | Your core claim: percentile-based advantage needs direct comparison literature |

---

## 📋 Recommended Citation Structure (Final)

| Section | Papers to Cite |
|---------|----------------|
| **Introduction** | Hao (2013, 2014), Rajsekhar (2015), Popat (2021), Adeyeri (2023) |
| **Methods** | Hao (2014), Zhang (2018), Demirel (2018, conditional), Mizukami (2019, conditional), **[SSI Reference]**, **[Recharge Drought]** |
| **Results** | — |
| **Discussion** | Hao (2013, 2014), Rajsekhar (2015), Popat (2021), Terzi (2025), Asad (2026, cautious), **[Percentile vs. Standardized]** |
| **Validation** | Stahl (2026) |

---

## 🔍 Priority Search Queries (to fill gaps)

| Priority | Query | Gap Addressed |
|----------|-------|---------------|
| 🔴 **High** | "Vicente-Serrano Standardized Streamflow Index SSI original" | SSI reference |
| 🔴 **High** | "groundwater drought index percentile recharge" | Recharge drought |
| 🔴 **High** | "percentile-based vs standardized drought index comparison" | Percentile vs. standardized |
| 🟡 **Medium** | "Adeyeri 2023 multivariate drought monitoring propagation" | Verify DOI/OA |
| 🟡 **Medium** | "Zhang 2018 nonparametric integrated agrometeorological drought" | Verify DOI/OA |

---

## 📊 Literature Coverage Map

| Component / Aspect | Covered Papers | Missing Papers |
|--------------------|----------------|----------------|
| **Multivariate Concept** | Hao (2013, 2014), Rajsekhar (2015), Popat (2021) | — |
| **Nonparametric / Percentile** | Hao (2014), Terzi (2025) | **[Percentile vs. Standardized comparison]** |
| **Hydrological (SM+Q)** | Popat (2021), Rajsekhar (2015) | — |
| **3-Component (SM+Recharge+Q)** | ❌ None | **Your innovation** (no direct precedent) |
| **Recharge / Groundwater** | ❌ None | **[Recharge drought index]** |
| **SSI Methodology** | ❌ None | **[SSI reference paper]** |
| **Validation (Impacts)** | Stahl (2026) | — |
| **mHM Methods** | Demirel (2018), Mizukami (2019) | — |

---

## 🎯 Your Innovation Statement (Based on Matrix)

> *"Hao & AghaKouchak (2013, 2014) introduced parametric and nonparametric Multivariate Standardized Drought Index (MSDI) frameworks coupling precipitation and soil moisture. Rajsekhar et al. (2015) extended multivariate drought assessment to four variables (precipitation, runoff, soil moisture, evapotranspiration) using information theory. Popat & Döll (2021) proposed a deficit-anomaly framework combining soil moisture and streamflow. However, no existing index couples three purely hydrological components (soil moisture, recharge, discharge) using a percentile-based approach validated against impact data. We address this gap with the Matrix Drought Index (MDI), quantifying propagation lags and validating against the European Drought Impacts Database (Stahl et al., 2026)."*

---

**Last Updated:** 2026-03-21 16:15 CET
**For:** PhD Paper #1 Literature Review
**Next Actions:**
1. Search for SSI reference paper (Vicente-Serrano)
2. Search for recharge/groundwater drought indices
3. Search for percentile vs. standardized comparison papers
4. Verify Adeyeri (2023) and Zhang (2018) DOIs
5. Consolidate all BibTeX entries (90+ papers)
