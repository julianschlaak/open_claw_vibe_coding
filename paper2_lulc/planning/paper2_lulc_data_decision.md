# Paper #2 LULC Data Decision Note — CORINE for Saxony

**Status:** Harte Entscheidungsnotiz (für Implementierungs-Start)  
**Datum:** 2026-03-13  
**Entscheidung:** CORINE Land Cover 1991–2024 (6 Snapshots)

---

## 1. Entscheidung

**Gewählte LULC-Datenbasis:**
> **CORINE Land Cover (CLC)** — 6 Snapshots: 1991, 2000, 2006, 2012, 2018, 2024

**Alternativen verworfen:**
- MODIS Land Cover (MCD12Q1): Annual, but different classification (IGBP), less suitable for Europe
-混合 (CORINE + MODIS): Higher complexity, classification mismatch risk
- CLC Plus: Not available for full 1991–2024 period

---

## 2. Begründung

### 2.1 Warum CORINE für Sachsen?

| Kriterium | CORINE | MODIS | Bewertung |
|-----------|--------|-------|-----------|
| **Klassenlogik** | Europa-spezifisch (44 Level-3 Klassen) | Global (IGBP, 17 Klassen) | ✅ CORINE besser für Deutschland |
| **Zeitliche Konsistenz** | 1991–2024 (6 Snapshots, gleiche Methodik) | 2000–2024 (annual, aber Klassifikationswechsel) | ✅ CORINE konsistenter |
| **Räumliche Auflösung** | 100m (Level-3), 25ha MAU | 500m (MCD12Q1) | ✅ CORINE feiner |
| **Sachsen-Eignung** | EEA-Standard, Deutschland vollständig abgedeckt | Global, aber Europa weniger detailliert | ✅ CORINE regional besser |
| **mHM-Kompatibilität** | Koycegiz 2024 verwendete MODIS, aber CORINE für Europa üblich | Koycegiz 2024 (Türkei, MODIS) | ⚠️ Beide machbar, CORINE für Europa bevorzugt |
| **Verfügbarkeit** | Kostenlos (EEA), 1991–2024 vollständig | Kostenlos (NASA), 2000–2024 | ✅ CORINE längere Periode (1991 Start) |

---

### 2.2 Warum 6 Snapshots (nicht annual interpoliert)?

**Option A: 6 Snapshots (step-function)**
- LULC ändert sich nur an Snapshot-Jahren (1991, 2000, 2006, 2012, 2018, 2024)
- Dazwischen: konstante LULC

**Option B: Annual interpolation (linear)**
- LULC interpoliert zwischen Snapshots (jährliche Änderung)

**Entscheidung: Option A (6 Snapshots, step-function)**

**Begründung:**
1. **Ehrliche Unsicherheit:** CORINE ist nur an Snapshot-Jahren beobachtet. Interpolation suggeriert Präzision, die nicht existiert.
2. **Klassifikations-Artefakte:** CORINE classification changes between versions may create artificial trends. Linear interpolation amplifies these artifacts.
3. **mHM-Präzedenz:** Koycegiz 2024 used annual MODIS, but CORINE has coarser temporal resolution — should not over-interpret.
4. **Prozess-Fokus:** Unser Paper testet Prozessverbesserung (Interception), nicht LULC-Rekonstruktion. Step-function ist konservativer und defensiver.

**Umsetzung:**
```
For t in [1991, 1999]: LULC = CORINE_1991
For t in [2000, 2005]: LULC = CORINE_2000
For t in [2006, 2011]: LULC = CORINE_2006
For t in [2012, 2017]: LULC = CORINE_2012
For t in [2018, 2023]: LULC = CORINE_2018
For t in [2024]:        LULC = CORINE_2024
```

---

## 3. Datenverarbeitung (Harmonization Rules)

### 3.1 Klassifikation-Harmonisierung

**Problem:** CORINE nomenclature changed between versions (1991, 2000, 2006, 2012, 2018, 2024).

**Lösung:** CORINE 2018 nomenclature als Referenz; ältere Versionen gemappt.

**Mapping-Beispiele:**
| CORINE 1991 Class | CORINE 2018 Equivalent | Anmerkung |
|-------------------|------------------------|-----------|
| 2.1 Arable land | 2.1 Arable land | No change |
| 2.3 Grassland | 2.3 Pastures + 3.2 Natural grasslands | Merged |
| 3.1 Forest (mixed) | 3.1.1 Broad-leaved + 3.1.2 Coniferous + 3.1.3 Mixed | Split |

**Implementierung:**
Lookup table (1991→2018, 2000→2018, 2006→2018, 2012→2018, 2018→2018, 2024→2018).

---

### 3.2 Aggregation auf 4 mHM-Klassen

**CORINE Level-3 (44 Klassen) → mHM (4 Oberklassen):**

| mHM Klasse | CORINE Level-3 Klassen (IDs) |
|------------|------------------------------|
| **Forest** | 3.1.1 (Broad-leaved), 3.1.2 (Coniferous), 3.1.3 (Mixed), 3.2.2 (Moors/heath), 3.2.4 (Transitional woodland) |
| **Grassland** | 2.3.1 (Pastures), 3.2.1 (Natural grasslands), 3.2.2 (Moors/heath), 3.3.3 (Sparsely vegetated) |
| **Cropland** | 2.1.1 (Arable land), 2.1.2 (Permanent crops), 2.4 (Heterogeneous agricultural) |
| **Urban** | 1.1 (Urban fabric), 1.2 (Industrial/commercial), 1.3 (Mine/dump), 1.4 (Artificial surfaces) |

**Code:**
```python
# Pseudocode: CORINE → mHM mapping
corine_to_mhm = {
    # Forest
    '3.1.1': 'Forest', '3.1.2': 'Forest', '3.1.3': 'Forest',
    '3.2.2': 'Forest', '3.2.4': 'Forest',
    # Grassland
    '2.3.1': 'Grassland', '3.2.1': 'Grassland', '3.3.3': 'Grassland',
    # Cropland
    '2.1.1': 'Cropland', '2.1.2': 'Cropland', '2.4.1': 'Cropland', '2.4.2': 'Cropland', '2.4.3': 'Cropland',
    # Urban
    '1.1.1': 'Urban', '1.1.2': 'Urban', '1.2.1': 'Urban', '1.2.2': 'Urban', '1.3.1': 'Urban', '1.3.2': 'Urban', '1.3.3': 'Urban', '1.4.1': 'Urban', '1.4.2': 'Urban',
}
```

---

### 3.3 Räumliche Harmonisierung

**Auflösung:**
- CORINE native: 100m (Level-3)
- mHM default: 1km × 1km (or 5km × 5km, depending on setup)
- **Entscheidung:** CORINE resampled to 1km × 1km (majority rule)

**Projektion:**
- CORINE: ETRS89 / UTM Zone 33N (EPSG:25833)
- mHM: same (EPSG:25833)
- **Keine Transformation nötig** (Sachsen in Zone 33N)

**Resampling rule:**
```
For each 1km × 1km mHM grid cell:
  LULC = mode(CORINE_100m cells within 1km cell)
```

---

### 3.4 Qualitätskontrolle (LULC Artefakte)

**Risiken:**
1. **Classification change:** CORINE 1991 used different methodology than 2018 — may create artificial jumps.
2. **Edge effects:** Catchment boundaries may show suspicious LULC trends (classification artifacts, not real change).
3. **Urban expansion:** Some "urban" increases may reflect improved detection, not real urbanization.

**Gegenmaßnahmen:**
1. **Visual inspection:** Plot LULC time series for each catchment — flag suspicious jumps.
2. **Smoothing rule:** If single-year jump >20% cover change, flag for review (may be artifact).
3. **Quality flag:** Add `LULC_quality_flag` per catchment (1 = clean, 2 = minor artifacts, 3 = major artifacts — exclude).

**Beispiel (Pseudo-Code):**
```python
def check_lulc_artifact(cumulative_lulc_series, threshold=0.20):
    # Check for single-year jumps >20%
    for year in [2000, 2006, 2012, 2018, 2024]:
        prev_year = previous_corine_year(year)
        delta = abs(lulc_fraction[year] - lulc_fraction[prev_year])
        if delta > threshold:
            return FLAG_SUSPICIOUS
    return FLAG_CLEAN
```

---

## 4. LAI-Daten (Ergänzung zu CORINE)

**LAI-Quelle:** MODIS MOD15A2H (500m, 8-day)

**Verarbeitung:**
1. **Periode:** 2000–2020 (Klimatologie)
2. **Saisonale Aggregation:** 3-Monats-Mittel (DJF, MAM, JJA, SON)
3. **LULC-spezifisch:** LAI aggregated per mHM class (Forest, Grassland, Cropland, Urban)
4. **1991–1999:** Use 2000–2020 climatology (stationary approximation)

**LAI-Tabelle (geplant):**

| LULC | DJF | MAM | JJA | SON |
|------|-----|-----|-----|-----|
| Forest | 1.5 | 3.5 | 5.0 | 3.0 |
| Grassland | 0.8 | 2.0 | 3.0 | 1.5 |
| Cropland | 0.3 | 2.0 | 4.0 | 1.0 |
| Urban | 0.2 | 0.3 | 0.3 | 0.2 |

*(Werte vorläufig — nach MODIS-Aggregation zu aktualisieren)*

---

## 5. Risiken und Unsicherheiten

| Risiko | Wahrscheinlichkeit | Auswirkung | Gegenmaßnahme |
|--------|-------------------|------------|---------------|
| **CORINE classification artifacts** | Moderat | Hoch (false LULC trends) | Visual inspection, smoothing rules, quality flags |
| **1991–1999 LAI unsicher** | Hoch | Moderat (early period ET uncertain) | Climatology (2000–2020 average), documented limitation |
| **Resampling smoothing** | Hoch | Moderat (local variability lost) | 1km resolution (not 5km), majority rule |
| **4-class aggregation** | Hoch | Moderat (within-class variability lost) | Documented limitation; Laub/Nadel optional Phase 2 |
| **LULC-Q nicht sensitiv** | Hoch (expected per Koycegiz) | Moderat (Q similar across M0-M2) | Multi-variable focus (ET, SM primary) |

---

## 6. Nächste Schritte (Daten-Pipeline)

| Schritt | Dauer | Deliverable |
|---------|-------|-------------|
| **1. CORINE download** (1991, 2000, 2006, 2012, 2018, 2024) | 1 week | 6 GeoTIFFs (Sachsen-Clip) |
| **2. Harmonization** (nomenclature mapping) | 3 days | Lookup table (1991→2018, etc.) |
| **3. Aggregation** (CORINE → 4 mHM classes) | 2 days | Mapping script (Python) |
| **4. Resampling** (100m → 1km) | 2 days | 6 rasters (1km, UTM33N) |
| **5. Catchment masking** (3-5 pilot catchments) | 2 days | Catchment-specific LULC time series |
| **6. Quality control** (artifact check) | 2 days | Quality flags per catchment |
| **7. LAI climatology** (MODIS aggregation) | 1 week | LAI table (4 classes × 4 seasons) |

**Summe:** ~3 Wochen (vollständige LULC-Pipeline)

---

## 7. Fazit

**CORINE 1991–2024 (6 Snapshots) ist die robuste Wahl für Sachsen.**

**Vorteile:**
- Europa-spezifische Klassifikation (besser als MODIS IGBP)
- 1991 Start (vollständige 30-Jahre-Periode)
- Konsistente Methodik (EEA-Standard)
- Koycegiz 2024 precedent (dynamic LULC in mHM, though MODIS)

**Risiken:**
- 6-Jahres-Auflösung (nicht annual)
- Classification artifacts zwischen Versionen
- LAI nur 2000+ (1991–1999 Klimatologie)

**Umgang:**
- Step-function (nicht linear interpoliert)
- Quality control (visual inspection, flags)
- Multi-variable evaluation (ET, SM — nicht nur Q)

---

**Entscheidung final.** Nächster Schritt: CORINE download + Harmonization (AP2).

**Word Count:** ~1,800 (1-2 pages)
