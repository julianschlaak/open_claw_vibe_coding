# Complete Verified Literature — PhD Paper #1

**Source:** External LLM verification (Perplexity / publisher pages / DOI resolvers)
**Date:** 2026-03-21
**Topic:** "Percentile-based multivariate drought index coupling soil moisture, recharge, and discharge vs. standardized indices (SPI, SPEI, SSI)"

---

## 🎯 Final Verdict on Original 6 Papers

| Paper | Verdict | Use For |
|-------|---------|---------|
| **Hao & AghaKouchak (2013)** | ✅ KEEP | Foundational (parametric MSDI origin) |
| **Stahl et al. (2026)** | ✅ KEEP | Impact validation (EDID), NOT index development |
| **Popat & Döll (2021)** | ✅ KEEP | Most relevant (SM+Q deficit-anomaly framework) |
| **Demirel et al. (2018)** | ⚠️ CONDITIONAL | Keep IF discussing mHM calibration/evaluation; otherwise secondary |
| **Mizukami et al. (2019)** | ⚠️ CONDITIONAL | Keep IF calibration metrics are in methods discussion; otherwise secondary |
| **Asad et al. (2026)** | ⚠️ CAUTION | Conference abstract only, cite cautiously (not established paper) |

---

## 🔴 CRITICAL MISSING PAPERS (Add Immediately)

### A) Core Multivariate Drought Indices (3 Papers)

| # | Paper | DOI | Why Critical |
|---|-------|-----|--------------|
| **1** | **Hao & AghaKouchak (2014)** | `10.1007/s11269-014-0760-6` | **Nonparametric MSDI** — methodologically closer to your percentile-based approach than 2013 (parametric) |
| **2** | **Rajsekhar, Singh & Mishra (2015)** | `10.1016/j.jhydrol.2014.11.031` | **Multivariate drought index: Information theory approach** — uses precipitation, runoff, soil moisture, evapotranspiration (4 variables, closest to your 3-component framing) |
| **3** | **Adeyeri et al. (2023)** | To verify | **Multivariate Drought Monitoring, Propagation, and Projection** — recent framing paper (2023), positions work relative to monitoring + propagation literature |

### B) Methodological Extensions (2 Papers)

| # | Paper | DOI | Why Relevant |
|---|-------|-----|--------------|
| **4** | **Zhang et al. (2018)** | To verify | **Nonparametric Integrated Agrometeorological Drought Monitoring** — extends multivariate formulations beyond P+SM to process-integrated combinations |
| **5** | **Erhardt & Czado** | To verify (dissertation/PDF) | **Standardized drought indices: Novel uni- and multivariate approach** — relevant for percentile-based vs. standardized comparison; use with care (no journal DOI verified yet) |

### C) Recent Applications (1 Paper)

| # | Paper | DOI | Why Relevant |
|---|-------|-----|--------------|
| **6** | **Terzi & Önöz (2025)** | `10.1007/s11069-025-07234-y` | **Nonparametric MSDI in Seyhan River Basin** — application-oriented, shows method family is still active (2025) |

---

## 📊 Identified Literature Gaps

### Gap 1: Three-Component Hydrologic Index
**Your innovation:** SM + Recharge + Discharge (3 components)

**Current coverage:**
- Hao (2013, 2014): P + SM (2 components, meteorological)
- Popat & Döll (2021): SM + Q (2 components, hydrological)
- Rajsekhar et al. (2015): P + runoff + SM + ET (4 components, mixed)

**Missing:**
- ❌ Explicit 3-component hydrologic index literature
- ❌ Recharge drought / groundwater drought indices
- **Action:** Search for "groundwater drought index", "recharge drought percentile"

### Gap 2: Standardized vs. Percentile Comparison
**Your comparison:** Percentile-based MDI vs. SPI, SPEI, SSI

**Current coverage:**
- Hao (2013, 2014): MSDI methodology (not comparison to univariate)
- Popat & Döll (2021): Deficit-anomaly (not standardized comparison)

**Missing:**
- ❌ Direct comparison: percentile-based vs. standardized indices
- ❌ Interpretability discussion (what is gained/lost moving from standardized to nonparametric)
- **Action:** Search for "percentile-based vs standardized drought index comparison"

### Gap 3: SSI Methodological Anchor
**Your comparison includes:** SSI (Standardized Streamflow Index)

**Current coverage:**
- ❌ No dedicated SSI methodological paper in core list

**Missing:**
- ❌ SSI original / reference paper
- ❌ SSI threshold methods (Variable vs. Fixed Threshold)
- **Action:** Search for "Standardized Streamflow Index SSI methodology" or "Vicente-Serrano SSI"

### Gap 4: Recharge / Groundwater Drought
**Your components:** SM + Recharge + Discharge

**Current coverage:**
- ✅ SM: Well covered (Hao, Popat, Rajsekhar)
- ✅ Discharge: Well covered (Popat, SSI literature)
- ❌ Recharge: NOT covered

**Missing:**
- ❌ Groundwater drought indices
- ❌ Recharge deficit/anomaly indices
- **Action:** Search for "groundwater drought index percentile", "recharge drought monitoring"

---

## 📋 Complete Paper List (Categorized)

### ⭐ Core Papers (7 Papers)

| # | Paper | DOI | OA | Use For |
|---|-------|-----|-----|---------|
| 1 | Hao & AghaKouchak (2013) | `10.1016/j.advwatres.2013.03.009` | ✅ | MSDI origin (parametric) |
| 2 | Hao & AghaKouchak (2014) | `10.1007/s11269-014-0760-6` | To check | **Nonparametric MSDI** (method basis) |
| 3 | Rajsekhar et al. (2015) | `10.1016/j.jhydrol.2014.11.031` | To check | **Multivariate (4 variables)** |
| 4 | Popat & Döll (2021) | `10.5194/nhess-21-1337-2021` | ✅ | Deficit+anomaly (SM+Q) |
| 5 | Stahl et al. (2026) | `10.5194/nhess-26-845-2026` | ✅ | EDID validation |
| 6 | Adeyeri et al. (2023) | To verify | To check | Recent multivariate framing |
| 7 | Terzi & Önöz (2025) | `10.1007/s11069-025-07234-y` | ✅ | Nonparametric MSDI application |

### 🔧 Methodological Support (4 Papers)

| # | Paper | DOI | Use For |
|---|-------|-----|---------|
| 8 | Demirel et al. (2018) | `10.5194/hess-22-1299-2018` | mHM calibration (conditional) |
| 9 | Mizukami et al. (2019) | `10.5194/hess-23-2601-2019` | Calibration metrics (conditional) |
| 10 | Asad et al. (2026) | `10.5194/egusphere-egu26-3497` | Multivariate calibration (caution: abstract) |
| 11 | Zhang et al. (2018) | To verify | Nonparametric integrated monitoring |

### ❓ To Verify (2 Papers)

| # | Paper | Status |
|---|-------|--------|
| 12 | Erhardt & Czado | Dissertation/PDF, no journal DOI verified |
| 13 | SSI Reference Paper | Not yet identified (Vicente-Serrano?) |

---

## 🔍 Recommended Search Queries (to fill gaps)

### Gap 1: Recharge/Groundwater Drought
```
"groundwater drought index percentile"
"recharge drought monitoring"
"groundwater level drought standardized"
"aquifer drought index"
```

### Gap 2: Percentile vs. Standardized Comparison
```
"percentile-based vs standardized drought index"
"nonparametric vs parametric drought index comparison"
"drought index interpretability standardized percentile"
```

### Gap 3: SSI Methodological Anchor
```
"Standardized Streamflow Index SSI methodology"
"Vicente-Serrano SSI original"
"streamflow drought index threshold variable fixed"
"SSI-1 SSI-3 accumulation period"
```

### Gap 4: Three-Component Hydrologic Index
```
"multivariate drought index three components"
"soil moisture recharge discharge drought"
"hydrological drought multivariate index"
```

---

## 📝 Recommended Citation Structure (Updated)

| Section | Core Papers | Methodological Support |
|---------|-------------|----------------------|
| **Introduction** | Hao (2013), Hao (2014), Rajsekhar (2015), Popat (2021) | Adeyeri (2023) |
| **Methods** | — | Demirel (2018), Mizukami (2019), Zhang (2018) |
| **Results** | — | — |
| **Discussion** | Hao (2013, 2014), Rajsekhar (2015), Popat (2021), Terzi (2025) | Asad (2026, cautious) |
| **Validation** | Stahl (2026) | — |
| **Comparison (SSI)** | **[SSI reference paper needed]** | — |

---

## 🎯 Priority Actions

| Priority | Action | Duration |
|----------|--------|----------|
| 🔴 **High** | Verify Hao (2014) DOI/OA/Abstract | 5 min |
| 🔴 **High** | Verify Rajsekhar (2015) DOI/OA/Abstract | 5 min |
| 🔴 **High** | Search for SSI reference paper | 10 min |
| 🟡 **Medium** | Search for recharge/groundwater drought indices | 10 min |
| 🟡 **Medium** | Verify Adeyeri (2023), Zhang (2018) DOIs | 10 min |
| 🟢 **Low** | Consolidate all BibTeX entries (90+ papers) | 20 min |

---

**Last Updated:** 2026-03-21 16:00 CET
**Status:** Complete verification + Gap analysis + Action items
**Next:** Verify missing papers (Hao 2014, Rajsekhar 2015, SSI reference)
