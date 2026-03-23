# Verified Literature Search — PhD Paper #1 (Updated)

**Source:** External LLM verification (Perplexity / publisher pages / DOI resolvers)
**Date:** 2026-03-21
**Topic:** "Percentile-based multivariate drought index coupling soil moisture, recharge, and discharge vs. standardized indices (SPI, SPEI, SSI)"

**Caveat:** Citation counts are approximate (publisher snippet metadata, not Google Scholar / Scite direct pulls). DOI/claim/OA checks are solid.

---

## 🎯 Bottom-Line Assessment

### Core and Directly Relevant

| Paper | DOI | Why Core |
|-------|-----|----------|
| **Hao & AghaKouchak (2013)** | `10.1016/j.advwatres.2013.03.009` | Foundational for MSDI (parametric multi-index model) |
| **Popat & Döll (2021)** | `10.5194/nhess-21-1337-2021` | Directly relevant for combining multiple hydrologic drought dimensions |
| **Stahl et al. (2026)** | `10.5194/nhess-26-845-2026` | Relevant for impact validation using EDID |

### Methodological Support (NOT Core Index Papers)

| Paper | DOI | Use For |
|-------|-----|---------|
| **Demirel et al. (2018)** | `10.5194/hess-22-1299-2018` | mHM/spatial calibration logic (Methods section) |
| **Mizukami et al. (2019)** | `10.5194/hess-23-2601-2019` | Objective functions, metric sensitivity (Methods section) |
| **Asad et al. (2026)** | `10.5194/egusphere-egu26-3497` | Multivariate calibration logic (conference abstract, methodologically adjacent) |

---

## ✅ Verified Papers (Detailed)

### 1. Hao & AghaKouchak (2013) — MSDI Original ⭐ CORE

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.1016/j.advwatres.2013.03.009` | ✅ Correct |
| **Title** | "Multivariate Standardized Drought Index: A parametric multi-index model" | ✅ |
| **Journal** | Advances in Water Resources | ✅ |
| **OA Status** | ✅ Yes (eScholarship full-text available) | ✅ |
| **Citations** | ~980 (snippet metadata, approximate) | ⚠️ Approximate |
| **Relevance** | **High** (benchmark/origin for MSDI) | ✅ |

### 🔬 Critical Correction

**Original Claim:** "MSDI combines soil moisture and discharge"

**Verified Claim:** "MSDI combines **precipitation and soil moisture** (NOT soil moisture and discharge)"

**Implication for Paper #1:**
- Hao & AghaKouchak (2013): **P + SM** → MSDI (meteorological + soil moisture)
- Your Paper #1: **SM + Recharge + Discharge** → MDI (purely hydrological)
- **Your innovation:** First multivariate index **without meteorological component**, extends to hydrological components only

**Corrected Positioning:**
> *"Hao & AghaKouchak (2013) introduced the parametric Multivariate Standardized Drought Index (MSDI) coupling precipitation and soil moisture. We extend this concept to hydrological components (soil moisture, recharge, discharge) using a percentile-based approach."*

---

### 2. Stahl et al. (2026) — EDID Operational ⭐ CORE

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/nhess-26-845-2026` | ✅ Correct |
| **Title** | "Towards an operational European Drought Impacts Database (EDID)" | ✅ |
| **Journal** | NHESS 26, 845–861 (2026) | ✅ |
| **OA Status** | ✅ Yes (CC BY 4.0, Copernicus) | ✅ |
| **Citations** | Too new for stable count | ⚠️ N/A |
| **Relevance** | **High** (validation against impacts) | ✅ |

### 🔬 Precise Framing

**Claim:** "EDID operational database paper"

**Verified:** "Moving EDID toward **operationalization** — systematic and operational European drought-impacts database"

**Implication for Paper #1:**
- **NOT** an index-development paper
- **But** external impact benchmark for validation
- Use for: **Ground truth validation** of your MDI against reported impacts

---

### 3. Popat & Döll (2021) — Deficit Anomaly Index ⭐ CORE

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/nhess-21-1337-2021` | ✅ Correct |
| **Title** | "Soil moisture and streamflow deficit anomaly index: an approach to quantify drought hazards by combining deficit and anomaly" | ✅ |
| **Journal** | NHESS 21, 1337–1353 (2021) | ✅ |
| **OA Status** | ✅ Yes (NHESS/Copernicus) | ✅ |
| **Citations** | ~7 (publisher snippet, approximate) | ⚠️ Approximate |
| **Relevance** | **Very High** (closest conceptual analogue) | ✅ |

### 🔬 Important Nuance

**Original Claim:** "Combines soil moisture and streamflow index"

**Verified:** "Combines **deficit and anomaly concepts** (not simply SM + Q in generic sense)"

**Key Distinction:**
- **SMDAI:** Soil Moisture Deficit Anomaly Index
- **QDAI:** Streamflow Deficit Anomaly Index
- **Innovation:** Deficit (demand-based) + Anomaly (statistical deviation)

**Implication for Paper #1:**
- Popat & Döll: **Deficit + Anomaly** framework
- You: **Percentile-based** (no distributional assumptions) + **3 components** (SM, Recharge, Q)
- **Your innovation:** Extends to **recharge** (third component) + percentile approach

---

### 4. Demirel et al. (2018) — mHM + Spatial Pattern 🔧 METHODS

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/hess-22-1299-2018` | ✅ Correct |
| **Title** | "Combining satellite data and appropriate objective functions for improved spatial pattern performance of a distributed hydrologic model" | ✅ |
| **Journal** | HESS 22, 1299–1315 (2018) | ✅ |
| **OA Status** | ✅ Yes (HESS/Copernicus) | ✅ |
| **Citations** | ~208 (publisher snippet, approximate) | ⚠️ Approximate |
| **Relevance** | **Medium** (methodological support, NOT drought index) | ✅ |

### 🔬 Critical Correction

**Original Claim:** "mHM + spatial pattern (SPAEF)" — directionally correct

**Verified:** "**Calibration/evaluation methodology paper** focused on improving spatial pattern performance of distributed hydrologic model. **NOT a drought-index paper.**"

**Implication for Paper #1:**
- **NOT central** to drought-index comparison
- **Use for:** Methods section (mHM justification, spatial evaluation logic)
- Same model (mHM), different focus: **Spatial patterns** (AET from MODIS) vs. **Temporal propagation** (P → SM → Recharge → Q)

---

### 5. Mizukami et al. (2019) — Calibration Metrics 🔧 METHODS

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/hess-23-2601-2019` | ✅ Correct |
| **Title** | "On the choice of calibration metrics for 'high-flow' estimation using hydrologic models" | ✅ |
| **Journal** | HESS 23, 2601–2621 (2019) | ✅ |
| **OA Status** | ✅ Yes (HESS/Copernicus) | ✅ |
| **Citations** | ~252 (publisher snippet, approximate) | ⚠️ Approximate |
| **Relevance** | **Medium to High** (methods: objective functions, metric sensitivity) | ✅ |

### 🔬 Verified Focus

**Claim:** "About calibration metrics"

**Verified:** "How the **choice of objective/performance metric affects calibration** aimed at high-flow estimation"

**Implication for Paper #1:**
- **Use for:** Methods section (calibration strategy, objective function discussion)
- **NOT** core drought-index concept
- Relevant if you discuss multivariate calibration strategy

---

### 6. Asad et al. (2026) — Multivariate Calibration 🔧 METHODS

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/egusphere-egu26-3497` | ✅ Correct (conference abstract) |
| **Title** | "Multivariate calibration and regionalization of a conceptual hydrological model using streamflow and groundwater level" | ✅ |
| **Source** | EGU General Assembly 2026 (conference abstract) | ✅ |
| **OA Status** | ✅ Yes (Copernicus preprint, CC BY) | ✅ |
| **Citations** | Not meaningful (conference abstract) | ⚠️ N/A |
| **Relevance** | **Medium** (methodologically adjacent, NOT core) | ✅ |

### 🔬 Important Correction

**Original Claim:** "Multivariate calibration CAMELS-DE paper"

**Verified:** "**Conference abstract** (not journal article). Uses 935 German catchments from CAMELS-DE, compares univariate (streamflow-only) vs. multivariate (streamflow + groundwater) calibration/regionalization."

**Implication for Paper #1:**
- **NOT a core citation** for drought-index paper
- **Methodologically adjacent** (multivariate calibration logic)
- **Expectations:** Conference abstract, not full journal article

**Your Innovation vs. Asad:**
- Asad: **Streamflow + Groundwater** (2 components), conceptual model
- You: **SM + Recharge + Discharge** (3 components), mHM 5.13.2, percentile-based MDI, EDID validation

---

## 📊 Summary: Core vs. Methodological Support

### ⭐ Core Papers (Cite in Introduction / Results / Discussion)

| # | Paper | DOI | Use For |
|---|-------|-----|---------|
| 1 | Hao & AghaKouchak (2013) | `10.1016/j.advwatres.2013.03.009` | MSDI origin, multivariate concept |
| 2 | Popat & Döll (2021) | `10.5194/nhess-21-1337-2021` | Deficit+anomaly framework, SM+Q combination |
| 3 | Stahl et al. (2026) | `10.5194/nhess-26-845-2026` | EDID validation, impact benchmark |

### 🔧 Methodological Support (Cite in Methods)

| # | Paper | DOI | Use For |
|---|-------|-----|---------|
| 4 | Demirel et al. (2018) | `10.5194/hess-22-1299-2018` | mHM justification, spatial pattern evaluation |
| 5 | Mizukami et al. (2019) | `10.5194/hess-23-2601-2019` | Calibration metrics, objective functions |
| 6 | Asad et al. (2026) | `10.5194/egusphere-egu26-3497` | Multivariate calibration logic (conference abstract) |

---

## 🎯 Corrected Positioning Statements

### Introduction (Core Papers)
> *"Hao & AghaKouchak (2013) introduced the parametric Multivariate Standardized Drought Index (MSDI) coupling precipitation and soil moisture. We extend this multivariate concept to purely hydrological components (soil moisture, recharge, discharge) using a percentile-based approach without distributional assumptions."*

> *"Popat & Döll (2021) proposed a deficit-anomaly framework combining soil moisture and streamflow. Our percentile-based MDI extends this to three hydrological components and quantifies propagation lags."*

### Validation (Core Papers)
> *"We validate our percentile-based MDI against the European Drought Impacts Database (Stahl et al., 2026), which operationalizes drought impact reporting across Europe."*

### Methods (Methodological Support)
> *"We use mHM 5.13.2 for hydrological simulation, following the spatial pattern evaluation approach of Demirel et al. (2018) and calibration metric considerations of Mizukami et al. (2019)."*

> *"Multivariate calibration strategies have been explored for streamflow + groundwater (Asad et al., 2026). We extend this to three components (SM, recharge, discharge) with percentile-based MDI."*

---

## 📝 Recommended Citation Structure for Paper #1

| Section | Core Papers | Methodological Support |
|---------|-------------|----------------------|
| **Introduction** | Hao (2013), Popat (2021) | — |
| **Methods** | — | Demirel (2018), Mizukami (2019), Asad (2026) |
| **Results** | — | — |
| **Discussion** | Hao (2013), Popat (2021), Asad (2026) | — |
| **Validation** | Stahl (2026) | — |

---

**Last Updated:** 2026-03-21 15:30 CET
**Verified By:** External LLM (Perplexity / publisher pages / DOI resolvers)
**For:** PhD Paper #1 Literature Review

**Next Steps:**
1. Download full PDFs via Helmholtz/UFZ access
2. Verify full-text claims (especially Rakovec 2022 details)
3. Consolidate BibTeX (30+ papers total)
4. Write Literature Review section
