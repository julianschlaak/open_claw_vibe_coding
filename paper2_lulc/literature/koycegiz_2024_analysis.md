# Koycegiz et al. (2024) — Detailed Analysis for Paper #2

**DOI:** `10.1007/s11269-024-03826-8`  
**Journal:** Water Resources Management (pending verification)  
**Status:** ⭐ **Most Direct Methodological Precedent** for Paper #2  
**Region:** Konya Endorheic Basin, Turkey (agriculturally intensive, irrigated)  
**Source:** Julian's Analysis (2026-03-12)

---

## 🎯 Kernaussage (Julian)

> **Koycegiz et al. 2024 ist für dein Paper sehr relevant. Nicht weil sie genau dein Interzeptionsproblem lösen, sondern weil sie zeigen, wie mHM mit zeitvariabler Landnutzung praktisch erweitert und gegen eine statische Variante getestet werden kann.**

**Das ist für dein Paper 2 wahrscheinlich der wichtigste direkte methodische Anschluss aus deiner Liste.**

---

## 🔧 Was sie konkret gemacht haben

**Titel:** (implies mHM extension for time-varying LULC + irrigation in strongly dynamic basin)

**Kernziel:**
- mHM erweitert, um in einem **stark landnutzungsdynamischen und bewässerten Becken** die **räumlich-zeitlichen Änderungen der Bewässerung und Landnutzung** abzubilden
- Damit **Groundwater-Anomalien realistischer simuliert** werden können

**Untersuchungsgebiet:**
- **Konya Endorheic Basin** (Türkei)
- Starke landwirtschaftliche Expansion
- Groundwater depletion issues

---

## 📐 Kernelemente (Was sie implementiert haben)

| Element | Umsetzung |
|---------|-----------|
| **mHM mit mehreren LULC-Karten** | Verschiedene Jahre als Input |
| **Jährlich variierende LULC** | MODIS LULC data (annual) |
| **Monatlich variierendes LAI** | Monthly LAI time series |
| **Explizites Bewässerungsschema** | Irrigation scheme added to mHM |
| **Vergleich** | Static LULC vs. Dynamic LULC |
| **Validierung** | Discharge + Groundwater level/anomaly data |

---

## 🔬 Methodische Lösung (Wie sie es gemacht haben)

### **1. Dynamische Landnutzung wirklich als Modellinput verwendet**

**Wichtig für dich:**
> Sie betonen explizit, dass **mHM im Gegensatz zu vielen anderen Modellen mehrere LULC-Karten aus verschiedenen Jahren als Input verarbeiten kann**.

**In ihrer Studie:**
- LULC-Zeitreihe aus **jährlichen MODIS-LULC-Daten**
- Zusätzlich: **monatlich variierendes LAI** eingebunden

**Transfer auf Paper #2:**
> Zeitvariable Landnutzung ist in mHM **prinzipiell machbar** — du kannst direkt anschließen!

---

### **2. Zwei zentrale mHM-Szenarien aufgesetzt**

**Sie unterscheiden (Abschnitt 4.3):**

| ID | Konfiguration | Beschreibung |
|----|---------------|--------------|
| **mHMF** | Fixed LULC | Feste LULC-Karte + langfristig gemitteltes monatliches LAI |
| **mHMV** | Variable LULC | Jährlich variierende LULC + monatlich variierendes LAI |

**Das ist methodisch für dich extrem wertvoll:**
> Das ist **fast direkt** deinem geplanten **M0/M1/M2-Denken** entsprechend!

**Für dein Paper — der entscheidende Transfer:**

| Koycegiz 2024 | Paper #2 (Your Design) |
|---------------|------------------------|
| mHMF (fixed LULC) | M0 (Standard-mHM, static LULC) |
| mHMV (variable LULC) | M1 (Dynamic LULC without process change) |
| - | M2 (Dynamic LULC + Interception scheme) |
| - | M3 (Scenario analysis) |

---

### **3. Anthropogenen Prozess explizit eingebaut (Irrigation)**

**Was sie gemacht haben:**
- Bewässerung in mHM eingebaut
- **Geschätzte Bewässerungsmenge pro Rasterzelle zum Niederschlag addiert**
- Anschließend als **Entnahme aus dem Grundwassersystem** berücksichtigt (Abschnitt 4.2)

**Bedeutung:**
> Das ist natürlich hydrologisch eine **pragmatische, nicht voll mechanistische Lösung**. Aber genau darin liegt die Lehre: Sie haben **keinen totalen Modellumbau** gemacht, sondern eine **gezielte, pragmatische Prozessergänzung**, die zum Problem des Beckens passt.

**Transfer auf Paper #2:**
> Genau das solltest du für dein Paper 2 ebenso tun — nur eben mit **Interception statt Bewässerung**!

---

## 🧪 Experimentdesign

### **5 Szenarien insgesamt**

**mHM-basiert (2):**
| ID | Beschreibung |
|----|--------------|
| **mHMF** | Feste LULC |
| **mHMV** | Variable LULC |

**GRACE/GLDAS-basiert (3):**
| ID | Beschreibung |
|----|--------------|
| **GRACE-GLDAS** | GRACE + GLDAS comparison |
| **GRACE-mHMF** | GRACE vs. mHMF |
| **GRACE-mHMV** | GRACE vs. mHMV |

**Logik dahinter:**
> Sie testen nicht nur, ob mHM "irgendwie läuft", sondern ob die **zeitvariable Landnutzung und die verbesserte Darstellung anthropogener Prozesse tatsächlich zu konsistenteren Wasserhaushaltsgrößen führen**.

**Transfer auf Paper #2:**
> Du brauchst ebenfalls eine **klare Vergleichslogik**, nicht nur eine neue Modellversion!

---

## 📊 Kalibrierung + Evaluation

### **Kalibrierung (gegen Streamflow)**

| Phase | Periode |
|-------|---------|
| **Warm-up** | 2002-2003 |
| **Calibration** | 2004-2015 |
| **Validation** | 2016-2019 |

**Algorithmus:** DDS (Dynamically Dimensioned Search)  
**Zielmetrik:** **KGE** (Kling-Gupta Efficiency)

---

### **Evaluation (Multi-Variable)**

| Variable | Data Source |
|----------|-------------|
| **Discharge (Q)** | Streamflow gauges |
| **Groundwater** | Groundwater level / anomaly data |
| **TWS** | GRACE satellite data (optional comparison) |
| **ET (aET)** | GLDAS comparison |

**Wichtig:**
> Sie evaluieren **nicht nur gegen Q**, sondern auch gegen **Grundwasser-Anomaliedaten** — das ist **Mehrgrößen-Evaluation** wie in deinem Paper #2 Design!

---

## 🔬 Wichtigste Ergebnisse (Kernaussagen)

### **1. Abflussgüte ist bei fester und variabler LULC ähnlich**

**Befund:**
> Die Streamflow-Performance von mHMF und mHMV ist insgesamt **ähnlich und zufriedenstellend** (Abschnitt 5.1, Radar-Grafik p. 8).

**Wissenschaftlich extrem interessant:**
> **Abfluss allein** hätte hier den Unterschied zwischen statischer und dynamischer LULC **kaum sichtbar gemacht**.

**Transfer auf Paper #2:**
> Wenn du **nur Q evaluierst**, könntest du den Mehrwert deiner Interception-Verbesserung **übersehen**!

---

### **2. Der Unterschied zeigt sich stärker in ET und Grundwasser**

**ET (aET):**
> Deutliche Unterschiede zu GLDAS. Die mHM-Simulationen liefern **deutlich höhere und plausiblere aET-Werte**; besonders **mHMV zeigt stärkere Trends** — die Autoren führen das direkt auf die **Einbindung der jährlich variierenden LULC** zurück (Abschnitt 5.3).

**Grundwasser:**
> **Variable LULC verbessert die Grundwasseranomalien deutlich** — das ist ihr **Hauptbefund**!

**Zahlen:**
| Metrik | mHMV (variable LULC) |
|--------|---------------------|
| **R²** | 0.840 |
| **NSE** | 0.822 |

**Schlüsselaussage:**
> Die Einbeziehung variabler Landbedeckung verbessert die Simulation der Wasserhaushaltskomponenten deutlich, **auch wenn das nicht unbedingt sofort im Abfluss sichtbar wird**.

---

### **3. Diskussion: Streamflow-Kalibrierung allein reicht nicht**

**Wortlaut (Discussion):**
> Sie zeigen ausdrücklich, dass **reine Streamflow-Kalibrierung** in den stärker veränderten landwirtschaftlichen Tieflandbereichen **nicht ausreicht**, weil dort Oberflächenbeobachtungen fehlen und die relevanten anthropogenen Effekte anders sichtbar werden.

**Deshalb:**
> Sie bewerten zusätzlich die **Groundwater Anomalies gegen In-situ-Brunnenmessungen**.

**Transfer auf Paper #2:**
> Das ist ein **sehr starkes Argument für Mehrgrößenbewertung** (Q, SM, ET, Recharge)!

---

## 💡 Was Koycegiz 2024 für Paper #2 liefert

### ✅ **Direkte methodische Unterstützung**

| Koycegiz-Element | Paper #2 Nutzung |
|------------------|------------------|
| **mHM kann multiple LULC-Karten** | ✅ Bestätigt: mHM supports time-varying LULC input |
| **MODIS annual LULC** | ✅ Similar to your CORINE approach (annual/6-year snapshots) |
| **Monthly LAI** | ✅ You plan seasonal LAI variation too |
| **mHMF vs. mHMV (static vs. dynamic)** | ✅ Direct precedent for your M0 vs. M1 vs. M2 design |
| **Pragmatic process addition (irrigation)** | ✅ Supports your interception approach (not full model overhaul) |
| **Multi-variable evaluation (Q + GW)** | ✅ Supports your Q + SM + ET + Recharge design |
| **KGE as metric** | ✅ Same metric in your design |

---

### ⚠️ **Was Koycegiz NICHT macht (deine Innovation)**

| Element | Koycegiz 2024 | Paper #2 (Your Contribution) |
|---------|---------------|------------------------------|
| **Process focus** | Irrigation (anthropogenic water addition) | **Interception** (LULC-sensitive storage) |
| **LULC process** | Dynamic LULC extent only | **Dynamic LULC + process-based interception** |
| **Interception** | ❌ Not addressed | ✅ Your main innovation |
| **Forest vs. Non-Forest** | ❌ Agricultural focus | ✅ Forest regeneration, land use transitions |
| **Regional context** | Turkey (Konya Basin) | **Saxony, Germany** (CAMELS-DE, Renner 2024 overlap) |

---

## 🎯 Transfer Statement (für Paper #2)

### **Introduction:**
> "Recent work has demonstrated that mHM can incorporate time-varying land use information to simulate hydrological impacts of land cover change (Koycegiz et al., 2024). Their study in the Konya Basin (Turkey) showed that dynamic LULC representation improved groundwater anomaly simulation compared to static LULC. However, their approach focused on irrigation as an anthropogenic process. We extend this by implementing a **process-based, LULC-sensitive interception module** that explicitly represents vegetation-mediated hydrological processes."

### **Methods:**
> "Following Koycegiz et al. (2024), we employ a multi-configuration design comparing static LULC (M0), dynamic LULC without process change (M1), and dynamic LULC with enhanced interception (M2). Unlike Koycegiz et al. who focused on irrigation, we address interception as a key LULC-sensitive process."

### **Discussion:**
> "Koycegiz et al. (2024) demonstrated the feasibility of dynamic LULC in mHM. Our study complements their work by showing that **process-based representation** (interception) further improves multi-variable consistency beyond dynamic LULC extent alone."

---

## 📋 **Direct Lessons for Paper #2 Implementation**

### **Technical Takeaways:**

| Lesson | Paper #2 Application |
|--------|---------------------|
| **mHM accepts multiple LULC maps** | ✅ Use CORINE 1991, 2000, 2006, 2012, 2018, 2024 |
| **Monthly LAI variation** | ✅ Implement seasonal LAI cycle per LULC class |
| **Static vs. Dynamic comparison** | ✅ M0 (static) vs. M1 (dynamic) vs. M2 (dynamic + interception) |
| **Pragmatic process addition** | ✅ Interception storage per LULC class (not full canopy physics) |
| **KGE as primary metric** | ✅ Use KGE for Q, SM, ET evaluation |
| **Multi-variable evaluation** | ✅ Q + SM + ET + Recharge (not just Q) |

---

### **Code Implementation Hints:**

**From Koycegiz 2024 (implied):**
- mHM input files: `mhm.nml`, `mhm_parameter.nml` need LULC map paths
- LULC maps: GeoTIFF or ASC format, same resolution as meteorological forcing
- LAI: Monthly tables per LULC class (can be parameter file)
- Interception: New parameter file or extension of existing LULC parameter table

**Your extension:**
- Interception storage capacity (`S_max`) per LULC class
- Seasonal variation (summer vs. winter, or monthly LAI-based)
- Forest vs. Grassland vs. Cropland vs. Urban differentiation

---

## 🧭 **Ehrliche Einschätzung zur Relevanz**

| Paper #2 Section | Koycegiz Usefulness |
|------------------|---------------------|
| **Introduction** | ⭐⭐⭐⭐ Strong (mHM dynamic LULC precedent) |
| **Study Area** | ⭐⭐ Limited (different region, but methodological transfer) |
| **Methods** | ⭐⭐⭐⭐⭐ **Essential** (direct mHM implementation precedent) |
| **Results** | ⭐⭐⭐⭐⭐ **Essential** (Q similar, ET/GW different — supports multi-variable eval) |
| **Discussion** | ⭐⭐⭐⭐⭐ Strong (position your interception innovation, multi-variable argument) |

---

## 💎 **Die Wichtigste Lehre (Gold für Paper #2)**

### **Kernaussage:**

> **Zeitvariable Landnutzungsinformationen in mHM können einen echten Mehrwert liefern, selbst wenn sich dieser nicht sofort deutlich in der Abflussgüte zeigt, sondern vor allem in anderen Wasserhaushaltskomponenten.**

---

### **Für dein Exposé / Paper — Direkter Transfer:**

| Koycegiz Finding | Paper #2 Application |
|------------------|---------------------|
| **Q similar (static vs. dynamic)** | Erwartbar: M0 vs. M1 vs. M2 könnten ähnliche Q-KGE haben |
| **ET different** | **SM + ET zeigen den Interception-Effekt!** |
| **Groundwater improved** | **Recharge zeigt den LULC-Effekt!** |
| **Streamflow calibration alone insufficient** | **Mehrgrößenbewertung ist notwendig!** |

---

### **Reviewer-Einwand Vorbeugung:**

**Typischer Einwand:**
> "Warum neue Modellkomplexität, wenn Q doch ähnlich bleibt?"

**Antwort (aus Koycegiz):**
> "Weil eine bessere Prozessrepräsentation unter LULC-Wandel vor allem die **interne Wasserbilanz und Mehrgrößen-Konsistenz** verbessern kann, **nicht nur Q**."

**Unterstützung:**
> Koycegiz zeigt: mHMF vs. mHMV haben ähnliche Q-Performance, aber **mHMV zeigt deutlich bessere Groundwater-Anomalien** (R² = 0.840, NSE = 0.822).

---

### **Paper #2 Evaluation-Design (aus Koycegiz abgeleitet):**

| Variable | Erwartetes Signal |
|----------|-------------------|
| **Q (KGE)** | M0 ≈ M1 ≈ M2 (similar, may not show difference) |
| **ET (KGE, Bias)** | M2 > M1 > M0 (interception effect visible) |
| **SM (KGE, Anomalie)** | M2 > M1 > M0 (soil moisture response) |
| **Recharge (NSE, R²)** | M2 > M1 > M0 (groundwater response) |

**Lesson:**
> Wenn du **nur Q bewertest**, könntest du den **Mehrwert deiner Interception-Verbesserung übersehen**!

---

## 📋 **Direct Lessons for Paper #2 Implementation** (Updated)

### **Technical Takeaways:**

| Lesson | Paper #2 Application |
|--------|---------------------|
| **mHM accepts multiple LULC maps** | ✅ Use CORINE 1991, 2000, 2006, 2012, 2018, 2024 |
| **Monthly LAI variation** | ✅ Implement seasonal LAI cycle per LULC class |
| **Static vs. Dynamic comparison** | ✅ M0 (static) vs. M1 (dynamic) vs. M2 (dynamic + interception) |
| **Pragmatic process addition** | ✅ Interception storage per LULC class (not full canopy physics) |
| **KGE as metric** | ✅ Use KGE for Q, SM, ET evaluation |
| **Multi-variable evaluation** | ✅ Q + SM + ET + Recharge (**not just Q!**) |
| **Q may not show difference** | ✅ **Evaluate SM, ET, Recharge primarily!** |
| **Groundwater/Storage response** | ✅ Recharge anomalies (like Koycegiz GW anomalies) |

---

## 🎯 **Bottom Line**

### **What Koycegiz solved:**

> Dynamic LULC in mHM using MODIS annual maps + monthly LAI, with pragmatic irrigation addition. Validated against streamflow (KGE) and groundwater anomalies.

**Key findings:**
1. **Q similar** (mHMF ≈ mHMV) — streamflow alone doesn't show the difference
2. **ET different** — mHMV shows stronger trends, attributed to dynamic LULC
3. **Groundwater improved** — mHMV: R² = 0.840, NSE = 0.822 (much better than static)
4. **Discussion:** Streamflow calibration alone is insufficient in changed landscapes

---

### **For your project:**

> This paper is the **most direct methodological precedent** for Paper #2. It shows that **mHM can handle time-varying LULC** and that **static vs. dynamic comparison** is feasible. Your innovation builds on this by adding **process-based interception** rather than irrigation.

**Critical lesson:**
> If you **only evaluate Q**, you might **miss the value** of your interception improvement! Koycegiz shows: Q similar, but **groundwater/recharge shows the LULC effect**.

---

### **Your claim:**

> "Koycegiz et al. (2024) demonstrated dynamic LULC in mHM with irrigation, showing that streamflow performance alone doesn't reveal LULC effects. We extend this by implementing **LULC-sensitive interception** as a key vegetation-mediated process, enabling improved simulation of **ET, soil moisture, and recharge** under land cover change — even when discharge performance remains similar."

---

### **Pre-empting Reviewer Objections:**

**Anticipated reviewer comment:**
> "Why add model complexity if Q remains similar?"

**Your response (based on Koycegiz):**
> "Koycegiz et al. (2024) showed that static vs. dynamic LULC in mHM produced similar streamflow performance (KGE), but dynamic LULC significantly improved groundwater anomaly simulation (R² = 0.840, NSE = 0.822). Similarly, our LULC-sensitive interception module improves internal water balance consistency (ET, SM, Recharge) even if discharge metrics remain comparable. Multi-variable evaluation is essential to detect process-based improvements under land cover change."

---

## 📚 **Citation Strategy**

**Primary use:**
- **Methods section** (mHM dynamic LULC feasibility)
- **Introduction** (recent mHM LULC work)
- **Discussion** (position your interception innovation vs. their irrigation focus)

**Key quote:**
> "While Koycegiz et al. (2024) addressed anthropogenic water addition (irrigation) in mHM with dynamic LULC, we address vegetation-mediated processes (interception) that are equally LULC-sensitive but remain underrepresented in current mHM implementations."

---

**Last Updated:** 2026-03-12 (Julian's Analysis)  
**Next:** Commit + Push, then integrate into paper2_design.md Methods section
