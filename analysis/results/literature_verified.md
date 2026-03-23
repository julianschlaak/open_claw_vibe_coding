# Verified Literature Search — PhD Paper #1

**Source:** External LLM verification (Perplexity / publisher pages / DOI resolvers)
**Date:** 2026-03-21
**Topic:** "Percentile-based multivariate drought index coupling soil moisture, recharge, and discharge vs. standardized indices (SPI, SPEI, SSI)"

**Caveat:** Citation counts are approximate (publisher snippet metadata, not Google Scholar / Scite direct pulls). DOI/claim/OA checks are solid.

---

## ✅ Verified Papers

### 1. Hao & AghaKouchak (2013) — MSDI Original

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.1016/j.advwatres.2013.03.009` | ✅ Correct |
| **Title** | "Multivariate Standardized Drought Index: A parametric multi-index model" | ✅ |
| **Journal** | Advances in Water Resources | ✅ |
| **OA Status** | ✅ Yes (eScholarship full-text available) | ✅ |
| **Citations** | ~980 (snippet metadata, approximate) | ⚠️ Approximate |
| **Relevance** | High (benchmark/origin for MSDI) | ✅ |

### 🔬 Critical Correction

**Original Claim:** "MSDI combines soil moisture and discharge"

**Verified Claim:** "MSDI combines **precipitation and soil moisture** (NOT soil moisture and discharge)"

**Implication for Paper #1:**
- Hao & AghaKouchak (2013): **P + SM** → MSDI
- Your Paper #1: **SM + Recharge + Discharge** → MDI
- **Your innovation:** Extends multivariate concept to **hydrological components** (not meteorological + SM)

**Corrected Positioning:**
> *"Hao & AghaKouchak (2013) introduced the parametric Multivariate Standardized Drought Index (MSDI) coupling precipitation and soil moisture. We extend this concept to hydrological components (soil moisture, recharge, discharge) using a percentile-based approach."*

---

### 2. Stahl et al. (2026) — EDID Operational

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/nhess-26-845-2026` | ✅ Correct |
| **Title** | "Towards an operational European Drought Impacts Database (EDID)" | ✅ |
| **Journal** | NHESS 26, 845–861 (2026) | ✅ |
| **OA Status** | ✅ Yes (CC BY 4.0, Copernicus) | ✅ |
| **Citations** | Too new for stable count | ⚠️ N/A |
| **Relevance** | High (validation against impacts) | ✅ |

### 🔬 Precise Framing

**Claim:** "EDID operational database paper"

**Verified:** "Moving EDID toward **operationalization** — systematic and operational European drought-impacts database"

**Implication for Paper #1:**
- **Not** an index-development paper
- **But** external impact benchmark for validation
- Use for: **Ground truth validation** of your MDI against reported impacts

---

### 3. Popat & Döll (2021) — Deficit Anomaly Index

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

### 4. Demirel et al. (2018) — mHM + Spatial Pattern

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/hess-22-1299-2018` | ✅ Correct |
| **Title** | "Combining satellite data and appropriate objective functions for improved spatial pattern performance of a distributed hydrologic model" | ✅ |
| **Journal** | HESS 22, 1299–1315 (2018) | ✅ |
| **OA Status** | ✅ Yes (HESS/Copernicus) | ✅ |
| **Citations** | ~135+ (publisher snippet) | ⚠️ Approximate |
| **Relevance** | High (mHM calibration, SPAEF metric) | ✅ |

### 🔬 Verified Focus

**Claim:** "mHM + spatial pattern performance"

**Verified:** "Satellite data (MODIS AET) + objective functions (KGE, SPAEF) for **spatial pattern calibration**"

**Implication for Paper #1:**
- Same model (mHM)
- Different focus: **Spatial patterns** (AET from MODIS) vs. **Temporal propagation** (P → SM → Recharge → Q)
- **Your innovation:** Temporal lag quantification vs. their spatial pattern optimization

---

### 5. Mizukami et al. (2019) — Calibration Metrics

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/hess-23-2601-2019` | ✅ Correct |
| **Title** | "Toward seamless large domain parameter estimation for hydrologic models" | ✅ |
| **Journal** | HESS 23, 2601–2621 (2019) | ✅ |
| **OA Status** | ✅ Yes (HESS/Copernicus) | ✅ |
| **Citations** | ~252+ (publisher snippet) | ⚠️ Approximate |
| **Relevance** | High (calibration metrics, mHM team) | ✅ |

---

### 6. Asad et al. (2026) — Multivariate CAMELS-DE

| Field | Value | Verified |
|-------|-------|----------|
| **DOI** | `10.5194/egusphere-egu26-3497` | ✅ Correct (preprint) |
| **Title** | "Multivariate calibration of streamflow and groundwater using 935 CAMELS-DE catchments" | ✅ |
| **Journal** | EGU General Assembly 2026 (preprint) | ✅ |
| **OA Status** | ✅ Yes (Copernicus preprint, CC BY) | ✅ |
| **Citations** | Too new (2026 conference) | ⚠️ N/A |
| **Relevance** | **Very High** (direct comparison) | ✅ |

### 🔬 Verified Comparison

**Your Paper #1 vs. Asad et al. (2026):**

| Aspect | Asad (2026) | You (Paper #1) |
|--------|-------------|----------------|
| **Components** | Streamflow + Groundwater (2) | SM + Recharge + Discharge (3) |
| **Method** | KGE-based calibration | Percentile-based MDI |
| **Catchments** | 935 CAMELS-DE | 456 CAMELS-DE (consistent period) |
| **Period** | Not specified | 1991–2020 (30 years) |
| **Validation** | KGE scores | EDID impacts |

**Your Innovation:**
- 3 components (not 2)
- Percentile-based (not KGE optimization)
- Impact validation (EDID)

---

## 📊 Summary Table

| # | Paper | DOI | OA | Claim Verified | Relevance |
|---|-------|-----|-----|----------------|-----------|
| 1 | Hao & AghaKouchak (2013) | `10.1016/j.advwatres.2013.03.009` | ✅ | ⚠️ Partial (P+SM, not SM+Q) | High |
| 2 | Stahl et al. (2026) | `10.5194/nhess-26-845-2026` | ✅ | ✅ Yes | High (validation) |
| 3 | Popat & Döll (2021) | `10.5194/nhess-21-1337-2021` | ✅ | ✅ Yes (nuance: deficit+anomaly) | Very High |
| 4 | Demirel et al. (2018) | `10.5194/hess-22-1299-2018` | ✅ | ✅ Yes | High |
| 5 | Mizukami et al. (2019) | `10.5194/hess-23-2601-2019` | ✅ | ✅ Yes | High |
| 6 | Asad et al. (2026) | `10.5194/egusphere-egu26-3497` | ✅ | ✅ Yes | Very High |

---

## 🎯 Corrected Positioning Statements

### Introduction
> *"Hao & AghaKouchak (2013) introduced the parametric Multivariate Standardized Drought Index (MSDI) coupling precipitation and soil moisture. We extend this multivariate concept to hydrological components (soil moisture, recharge, discharge) using a percentile-based approach without distributional assumptions."*

### Methods
> *"Popat & Döll (2021) proposed a deficit-anomaly framework combining soil moisture and streamflow. Our percentile-based MDI extends this to three hydrological components and quantifies propagation lags."*

### Discussion
> *"Asad et al. (2026) demonstrated multivariate calibration (streamflow + groundwater) for 935 CAMELS-DE catchments. Our study extends this to three components (SM, recharge, discharge) with percentile-based MDI validated against EDID impacts."*

### Validation
> *"Stahl et al. (2026) operationalized the European Drought Impacts Database (EDID). We use EDID as ground truth validation for our percentile-based MDI."*

---

**Last Updated:** 2026-03-21 15:15 CET
**Verified By:** External LLM (Perplexity / publisher pages / DOI resolvers)
**For:** PhD Paper #1 Literature Review
