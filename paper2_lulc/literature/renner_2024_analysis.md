# Renner et al. (2024) — Detailed Analysis for Paper #2

**DOI:** `10.5194/hess-28-2849-2024`  
**Journal:** Hydrology and Earth System Sciences (HESS), Vol. 28, pp. 2849-2867  
**Status:** ✅ DOI-verifiziert + Julian's Detailed Analysis (2026-03-12)  
**Region:** ⭐ **Sachsen!** 71 Catchments, 1951-2020  

---

## 🎯 Kernaussage (Julian)

> **Dieses Paper ist für dein Vorhaben deutlich relevanter als das vorherige, aber es löst dein Problem nur teilweise.**

**Der zentrale Punkt:**
- Sie implementieren **kein dynamisches LULC-Modul** in einem hydrologischen Modell
- Sie trennen beobachtete Änderungen in Runoff und ET **diagnostisch** in Klima- und Landoberflächen-Effekte auf

**Für Paper 2:** Sehr wertvoll — aber mehr als **konzeptionelle und diagnostische Vorlage** als als direkte technische Vorlage für mHM-Implementierung.

---

## 🔧 Wie haben sie es gelöst?

### **Ansatz: Diagnostisch, nicht modellstrukturell**

Sie arbeiten mit einem **gekoppelten Wasser- und Energiebilanz-Framework** auf Catchment-Ebene für 71 Einzugsgebiete in Sachsen (1951-2020).

**Verwendete Komponenten:**

| Element | Umsetzung |
|---------|-----------|
| **Wasserbilanz** | `P = ET + R + ΔS_w` (für längere Zeiträume näherungsweise: `ET = P - R`) |
| **Energiebilanz / Klimaantrieb** | Potenzielle Evaporation `E0` als Proxy für verfügbare Energie |
| **Rahmen** | Budyko-/Wasser-Energie-Rahmen zur Interpretation von ET- und Runoff-Änderungen |

---

## 📐 Kernidee: Joint Water–Energy Balance Diagram

### **1. Catchments in relativen Wasser- und Energiebilanzen darstellen**

**Zwei dimensionslose Größen:**

| Größe | Formel | Bedeutung |
|-------|--------|-----------|
| **Relative Water Balance** | `q = ET / P` | Anteil des Niederschlags, der verdunstet |
| **Relative Energy Balance** | `f = ET / E0` | Anteil der Energie, der für ET genutzt wird |

**Visualisierung:** Beide Größen gemeinsam in einem **joint water–energy balance diagram** plotten.

**Zweck:** Unterscheiden, ob Änderungen eher durch **Klimaänderung** oder durch **Landoberflächenänderung** kommen.

---

### **2. Änderungen geometrisch in Klima- und Landoberflächen-Effekt zerlegen**

**Auf Seite 3 und in Fig. 1:** Methodische Lösung der Zerlegung.

**Prinzip:**
- Ein Übergang von Zustand `(q0, f0)` zu `(q1, f1)` wird zerlegt in:
  - **Climate-Change Part** (`ΔRC`)
  - **Land-Surface-Change Part** (`ΔRL`)

**Berechnung:**
- Hypothetischer Zwischenzustand `(qb, fb)` bzw. `ETb` beschreibt, wie ET aussähe, wenn nur ein Teil der Änderung wirksam gewesen wäre
- **Eq. (3):** Berechnung des Zwischenzustands
- **Eq. (4):** Klimainduzierter Runoff-Change `ΔRC`
- **Eq. (5):** Land-Surface-induzierter Runoff-Change `ΔRL`

---

### **3. Dekadische Analyse statt hochfrequenter Modellierung**

**Methodische Wahl:**
- Arbeiten mit **Jahres- und Dekadenmitteln** (nicht monatlich/täglich)
- Zweck: Speicheränderungen `ΔS` glätten
- Vorteil: Langfristige Veränderungen robuster interpretierbar

**Begründung:**
> ET-Schätzung über `ET = P − R` wäre sonst zu stark durch Speicheränderungen verzerrt.

---

### **4. Landoberflächenänderung über Beobachtungen/Proxys erfasst (nicht mechanistisch)**

**Verwendete Daten für Landnutzung/Landoberfläche:**

| Datenquelle | Zweck |
|-------------|-------|
| **CORINE Land Cover** | LULC-Klassifikation |
| **Waldschadensinformationen** | CORINE class 324 "transitional scrub forest" als Proxy für Waldschäden |
| **Historische Canopy-Damage-Karten** | Forest disturbance tracking |

**Wichtig:**
> Sie simulieren **keinen Prozess wie Interzeption explizit neu**, sondern interpretieren beobachtete Wasserhaushaltsänderungen als Resultat von Landoberflächenänderungen.

---

## 🎓 Wissenschaftliche Lösung (Renner 2024)

**Ihre eigentliche Lösung:**

> Beobachtete Änderungen im Wasserhaushalt **diagnostisch so aufzuteilen**, dass klimatische und landoberflächenbezogene Beiträge **getrennt interpretiert** werden können.

**Was sie machen:**
- ✅ Diagnose
- ✅ Attribution
- ✅ Dekadenvergleich
- ✅ Budyko-basierte Interpretation
- ✅ Räumliche Musteranalyse über viele sächsische Catchments

---

## ⚖️ Renner 2024 vs. Paper #2 (mHM Interception)

| Aspekt | Renner 2024 | Paper #2 (Dein Ziel) |
|--------|-------------|---------------------|
| **Ansatz** | Diagnostisch / Attribution | Prozessbasiert / Simulation |
| **Modell** | Kein hydrologisches Modell (Budyko-Rahmen) | mHM (distributed, physically based) |
| **LULC** | Über Proxys erfasst (CORINE, canopy damage) | Dynamische LULC + Interception-Modul |
| **Zeitauflösung** | Jahres-/Dekadenmittel | Täglich / stündlich (mHM) |
| **Output** | Attributierte Änderungen (Klima vs. LULC) | Simulierte Wasserhaushaltskomponenten |
| **Innovation** | Attribution framework | Process-based interception implementation |

**Kernunterschied:**
> Renner macht **ex-post Attribution** (beobachtete Daten analysieren). Du willst **prozessbasierte Simulation** (mHM strukturell erweitern).

---

## 💡 Was Renner 2024 für Paper #2 liefert

### **✅ Konzeptionelle Unterstützung**

| Renner-Element | Paper #2 Nutzung |
|----------------|------------------|
| **71 sächsische Catchments** | ✅ Same region —可以直接 vergleichen |
| **1951-2020 Periode** | ✅ Overlap mit deinem 1991-2020 (30 Jahre) |
| **LULC als signifikanter Faktor** | ✅ Bestätigt: Landoberflächenänderung hat messbaren Effekt |
| **Forest regrowth effect** | ✅ Direkt relevant für Interception (Wald → mehr Interception) |
| **CORINE usage** | ✅ Same data source —可以直接 übernehmen |
| **Water-Energy Balance** | ✅ Conceptual framework for discussion |

### **⚠️ Was Renner NICHT liefert**

| Element | Renner | Paper #2 Bedarf |
|---------|--------|-----------------|
| **Interception implementation** | ❌ Nicht simuliert | ✅ Needed (mHM code) |
| **Dynamic LULC handling** | ❌ Nur als Proxy | ✅ Needed (time-varying maps) |
| **Process-based parameters** | ❌ Diagnostisch | ✅ Needed (storage capacity, LAI, etc.) |
| **mHM-spezifisches** | ❌ Kein Modell | ✅ Needed (nml changes, routines) |

---

## 📊 Wichtigste Ergebnisse (Renner 2024)

### **Hauptaussage: Wasserhaoalte in Sachsen sind nicht-stationär**

**Kernbefund:**
- **Jüngste Dekade 2011-2020** zeigt den **stärksten Rückgang des Runoffs**
- Rückgang wird in den meisten Catchments vor allem durch **zunehmende Aridität** erklärt
  - Sinkender Niederschlag (`P ↓`)
  - Steigende potenzielle Evaporation (`E0 ↑`)

**Aber:** Einige vor allem **bewaldete Mittelgebirgs-Catchments** zeigen stärkere Runoff-Rückgänge als klimatisch allein erklärbar.

**Interpretation:**
> Zusätzliche Effekte interpretieren die Autoren als **Landoberflächenwirkung**, insbesondere als anhaltende **Regeneration früher geschädigter Wälder**, die zu erhöhter tatsächlicher ET führt.

---

### **Dekaden-Vergleich (Fig. 9-11, p. 11-13)**

| Dekaden-Übergang | Dominanter Effekt |
|------------------|-------------------|
| **Frühere Dekaden** | Vielerorts dominieren **Landoberflächen-Effekte** |
| **2001-2010 → 2011-2020** | Vor allem **Klimaeffekte** |
| **Einzelne Catchments** | Zusätzliche starke **Landoberflächen-Signale** |

---

### **Schlüssoelpassage (Discussion)**

> Die Autoren schreiben explizit, dass in einigen Mittelgebirgscatchments die **ET-Zunahme auf wieder zunehmende Transpiration und Interzeptionsverdunstung** infolge von **Vegetationsregeneration** hindeutet.

**Das ist für dein Interception-Paper direkt anschlussfähig!** ⭐

---

### **Ergebnis-Übersicht**

| Ergebnis | Bedeutung für Paper #2 |
|----------|------------------------|
| **Largest decline: 2011-2020** | ✅ Relevant für deine 1991-2020 Periode (overlap) |
| **Forest headwaters: stronger decline** | ✅ Interception-relevant (Wald → mehr Interception → weniger Runoff) |
| **LULC effect detectable** | ✅ Bestätigt: Landoberflächenänderung ist messbar in Wasserhaushalt |
| **Climate vs. LULC separable** | ✅ Supports your M1 vs. M2 design (dynamic LULC vs. process change) |
| **71 catchments across Saxony** | ✅ Same region —可以直接 reference |
| **Vegetation regeneration → ET↑** | ✅ **Direct link to interception!** (Transpiration + Interception evaporation) |
| **Forest damage / recovery** | ✅ Supports your forest vs. non-forest contrast design |

---

## 🎯 Implikationen für Paper #2 Design

### **Wie Renner dein Design unterstützt**

| Paper #2 Element | Renner-Support |
|------------------|----------------|
| **Study Area (Saxony)** | ✅ Renner used 71 catchments — same region, credible |
| **Period (1991-2020)** | ✅ Overlap (1991-2020 vs. 1951-2020) —可以直接 compare |
| **LULC effect hypothesis (H1-H4)** | ✅ Renner shows LULC effect is detectable |
| **Forest vs. Non-Forest contrast** | ✅ Renner: "Forest headwaters show stronger decline" |
| **Multi-variable evaluation (Q, ET, SM)** | ✅ Renner uses P, ET, R — similar water balance approach |
| **Dynamic LULC rationale** | ✅ Renner shows LULC change has measurable impact |

### **Wie Renner deine Innovation abgrenzt**

**Dein Claim (Paper #2):**
> "Renner et al. (2024) attributed LULC effects diagnostically using water-energy balance. We advance this by **implementing a process-based interception module in mHM** that explicitly simulates LULC-sensitive interception dynamics, enabling **forward simulation** rather than ex-post attribution."

**Unterschied:**
- Renner: **Diagnostic** (what happened?)
- Du: **Process-based** (how does it work? can we simulate it?)

---

## 📝 Citation-Strategie für Paper #2

### **Introduction:**
> "Recent work in Saxony has demonstrated that land surface changes significantly affect catchment water balance (Renner et al., 2024). However, their diagnostic attribution approach does not enable forward simulation of LULC change impacts. We address this gap by implementing a dynamic, LULC-sensitive interception module in mHM."

### **Methods:**
> "Our study area overlaps with Renner et al. (2024), covering XX catchments in Saxony over 1991-2020. While Renner used a water-energy balance framework for attribution, we employ process-based simulation with dynamic LULC and explicit interception."

### **Discussion:**
> "Renner et al. (2024) detected LULC effects diagnostically. Our process-based approach shows similar patterns but enables scenario analysis (afforestation, deforestation) that diagnostic methods cannot provide."

---

## ✅ Fazit: Renner 2024 für Paper #2

| Kategorie | Einschätzung |
|-----------|--------------|
| **Relevanz** | ⭐⭐⭐⭐⭐ **Sehr hoch** (Sachsen, same period, LULC effect confirmed) |
| **Direkte Übernahme** | ⚠️ **Limited** (diagnostic ≠ process-based) |
| **Konzeptionelle Unterstützung** | ✅ **Strong** (water-energy balance, LULC attribution) |
| **Citation-Würdigkeit** | ✅ **Must cite** (regional context, validates LULC effect) |
| **Innovation-Abgrenzung** | ✅ **Clear** (diagnostic vs. process-based simulation) |

---

## 🎯 **Drei Funktionen für Paper #2**

### **A. Introduction-Zitat**

**Zweck:** Um zu zeigen, dass Sachsen hydrologisch bereits klare Signale von Klima- und Landoberflächenänderungen zeigt.

**Formulierung:**
> "Recent hydrological changes in Saxony (1951-2020) show strong non-stationarity, with the 2011-2020 decade exhibiting the strongest runoff decline. While most catchments show climate-driven patterns (decreased precipitation, increased potential evaporation), forested headwater catchments display additional runoff reductions attributable to land surface changes, particularly forest regeneration (Renner et al., 2024)."

---

### **B. Argument für Prozessfokus: Interception**

**Zweck:** Weil das Paper Waldregeneration explizit mit erhöhter ET sowie vermutlich stärkerer Transpiration/Interzeptionsverdunstung verbindet.

**Formulierung:**
> "Renner et al. (2024) attribute increased ET in forested catchments to vegetation regeneration, specifically noting enhanced transpiration and interception evaporation. This provides empirical evidence that interception processes are hydrologically relevant in Saxony, motivating our process-based implementation of LULC-sensitive interception in mHM."

---

### **C. Fallstudien-Design**

**Zweck:** Catchments ableiten aus Renner's 71-ceaeet dataset:

| Catchment-Typ | Kriterien (von Renner) |
|---------------|------------------------|
| **Stark bewaldet / Waldschaden-Regeneration** | High forest cover, historical forest damage, CORINE class 324 (transitional scrub forest) |
| **Landwirtschaftlich geprägt** | Low forest cover, agricultural dominance |
| **Niedrigland vs. Mittelgebirge** | Elevation contrast (Table A1) |
| **Unterschiedliche Aridität** | P/E0 ratio variation |
| **Geologie / Grundwassereinfluss** | Geological units, baseflow contribution |

**Practical use:**
- Pilot catchments selection
- Contrast group formation (forest vs. non-forest, lowland vs. highland)
- Target catchments with known forest regeneration signal

---

## 📝 **Clean Transfer Statement (für Paper #2)**

> "Previous observational studies in Saxony demonstrate that runoff changes cannot be explained solely by climate forcing, and that land surface changes—particularly in forested catchments—generate significant additional effects on ET and runoff (Renner et al., 2024). However, these effects have been analyzed primarily through diagnostic attribution frameworks. A process-based modeling approach that explicitly integrates time-varying land use information into simulation is currently lacking. This study addresses this gap by implementing a dynamic, LULC-sensitive interception module in mHM, enabling forward simulation of land cover change impacts rather than ex-post attribution."

---

## ⚠️ **Was Renner NICHT löst (deine Innovation)**

| Element | Renner 2024 | Paper #2 (Your Contribution) |
|---------|-------------|------------------------------|
| **Dynamic LULC in hydrological model** | ❌ No | ✅ Yes (time-varying CORINE in mHM) |
| **Process-based interception** | ❌ No | ✅ Yes (LULC-class specific storage) |
| **Time-varying parameterization** | ❌ No | ✅ Yes (seasonal, LULC-dynamic) |
| **Explicit land use transition simulation** | ❌ No | ✅ Yes (afforestation, deforestation scenarios) |
| **Multi-variable model calibration under LULC change** | ❌ No | ✅ Yes (Q, SM, ET, Recharge) |

**Your claim:**
> "Renner et al. (2024) demonstrate that land surface changes are important. We show **how to represent a central component of this effect explicitly in mHM** through time-varying LULC and LULC-sensitive interception."

---

## 🧭 **Ehrliche Einschätzung zur Relevanz**

| Paper #2 Section | Renner Usefulness |
|------------------|-------------------|
| **Introduction** | ⭐⭐⭐⭐⭐ Essential (regional motivation, LULC effect confirmed) |
| **Study Area** | ⭐⭐⭐⭐⭐ Essential (71 catchments, Table A1, selection criteria) |
| **Methods** | ⭐⭐ Limited (diagnostic ≠ process-based) |
| **Results** | ⭐⭐⭐ Useful (comparison target, forest vs. non-forest contrast) |
| **Discussion** | ⭐⭐⭐⭐⭐ Essential (position your contribution vs. diagnostic work) |

---

## 🎯 **Bottom Line**

**How Renner solved it:**
> Diagnostic decadal analysis in water-energy framework, attributing observed ET and runoff changes to climate and land surface components. Land surface changes interpreted via CORINE and forest damage data—but **not process-based simulated in a hydrological model**.

**For your project:**
> This paper is a **strong regional and conceptual bridge** to your topic, but **not the technical solution itself**. It provides the **rationale** for why an mHM paper with dynamic LULC-sensitive interception is scientifically valuable for Saxony.

---

**Last Updated:** 2026-03-12 (Julian's Analysis + Detailed Transfer)  
**Next:** Commit + Push to GitHub, then integrate into paper2_design.md Introduction/Discussion sections
