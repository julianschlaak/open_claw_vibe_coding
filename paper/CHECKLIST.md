# PhD Paper #1 — Submission Checklist

**Titel:** "A Percentile-Based Multi-Component Drought Index for Hydrological Drought Monitoring in Central Europe"

**Status:** Rohfassung vollständig (9,400 Wörter) ✅  
**Datum:** 2026-03-05  
**Target Journal:** HESS (Hydrology and Earth System Sciences) oder Journal of Hydrology  
**First Author:** Julian Schlaak  
**Co-Authors:** [Noch zu definieren]

---

## 📝 **MANUSCRIPT STATUS**

| Abschnitt | Status | Wörter | File | Review Needed? |
|-----------|--------|--------|------|----------------|
| Abstract | ✅ Fertig | ~200 | `draft_v1/01_abstract.md` | ⏳ |
| Introduction | ✅ Fertig | ~950 | `draft_v1/02_introduction.md` | ⏳ |
| Methods | ✅ Fertig | ~1,850 | `draft_v1/03_methods.md` | ⏳ |
| Results | ✅ Fertig | ~2,800 | `draft_v1/04_results.md` | ⏳ |
| Discussion | ✅ Fertig | ~2,900 | `draft_v1/05_discussion.md` | ⏳ |
| Conclusions | ✅ Fertig | ~750 | `draft_v1/06_conclusions.md` | ⏳ |
| References | ✅ Fertig | ~30 Papers | `draft_v1/07_references.md` | ⏳ |

**Gesamt:** ~9,400 Wörter (Target: ~8,000 für HESS) ✅

---

## 🔧 **OFFENE PUNKTE (Priorität: HOCH)**

### 1. Figure-Referenzen prüfen ⚠️

**Problem:** Im Text referenzieren wir Figure 1-11 + Figure A-F. Müssen mit Plot-Dateinamen abgeglichen werden.

**Aktuelle Mapping:**
- Figure 1 → `01_drought_timeseries.png`
- Figure 2 → `02_heatmap_smi.png`
- Figure 3 → `03_heatmap_recharge.png`
- Figure 4 → `04_heatmap_discharge.png`
- Figure 5 → `05_discharge_analysis.png`
- Figure 6 → `06_correlation_matrix.png`
- Figure 7 → `07_drought_duration.png`
- Figure 8 → `08_seasonal_boxplots.png`
- Figure 9 → `09_lag_correlation.png`
- Figure 10 → `10_matrix_drought_index.png`
- Figure 11 → `11_discharge_metrics_timeseries.png`
- Figure A → `advanced/A_drought_propagation.png`
- Figure B → `advanced/B_event_duration_survival.png`
- Figure C → `advanced/C_interannual_variability.png`
- Figure D → `advanced/D_spatial_comparison.png`
- Figure E → `advanced/E_index_comparison_taylor.png`
- Figure F → `advanced/F_drought_onset_analysis.png`

**Aufgabe:** 
- [ ] Figure-Captions für alle 17 Plots schreiben
- [ ] Figure-Nummerierung im Text konsistent machen
- [ ] Entscheidung: Advanced Plots (A-F) als Hauptfiguren oder Supplement?

### 2. Tabellen formatieren ⚠️

**Problem:** Table 1-3 sind im Text als Markdown-Tabelle, müssen für Submission als echte Tabellen formatiert werden.

**Tabellen im Text:**
- Table 1: Catchment Characteristics (Section 2.1)
- Table 2: Model Performance Metrics (Section 3.1.1)
- Table 3: Drought Days by Index (Section 3.2.1)

**Aufgabe:**
- [ ] Table 1-3 als separate Files oder LaTeX-Tabellen exportieren
- [ ] Table-Captions schreiben
- [ ] Entscheidung: Weitere Tabellen hinzufügen? (z.B. Drought Events Summary)

### 3. Author-Liste & Affiliations ⚠️

**Aufgabe:**
- [ ] First Author festlegen (Julian Schlaak?)
- [ ] Co-Authors identifizieren (Betreuer? Kollegen?)
- [ ] Affiliations sammeln (Universität Leipzig? UFZ?)
- [ ] Corresponding Author markieren
- [ ] ORCID-IDs sammeln

### 4. Target Journal Entscheidung ⚠️

**Optionen:**
- **HESS** (Hydrology and Earth System Sciences)
  - Impact Factor: ~5.2
  - Open Access
  - Fokus: Hydrologie + Erdsystem
  - Paper-Länge: Flexible (dieses Paper passt gut)
  
- **Journal of Hydrology**
  - Impact Factor: ~4.5
  - Subscription oder Open Access
  - Fokus: Reine Hydrologie
  - Paper-Länge: Bis ~10,000 Wörter

- **Water Resources Research**
  - Impact Factor: ~4.6
  - Sehr prestigeträchtig
  - Fokus: Wasserressourcen-Forschung
  - Paper-Länge: Kürzer (~6,000-8,000 Wörter)

**Aufgabe:**
- [ ] Journal auswählen
- [ ] Author Guidelines lesen
- [ ] Formatierung anpassen (LaTeX? Word? PDF?)

---

## 📊 **DATA & CODE VERFÜGBARKEIT** ⚠️

### 5. Code-Repository ⚠️

**Status:** Code existiert in `/data/.openclaw/workspace/open_claw_vibe_coding/analysis/scripts/`

**Aufgabe:**
- [ ] Code auf GitHub/GitLab hochladen (öffentlich oder privat?)
- [ ] README.md für Repository schreiben
- [ ] License auswählen (MIT? GPL-3.0?)
- [ ] DOI via Zenodo erstellen (für citable code)
- [ ] Code-URL im Paper einfügen (Data Availability Statement)

### 6. Data Availability ⚠️

**Datenquellen:**
- **mHM Outputs:** Eigene Simulationen (~GB an Daily Outputs)
- **CAMELS-DE:** Öffentlich verfügbar (Addor et al., 2018)
- **EDID:** Öffentlich verfügbar (DOI: 10.6094/UNIFR/230922)
- **DWD Precipitation:** Lizenzbeschränkt (nicht öffentlich teilbar)

**Aufgabe:**
- [ ] Data Availability Statement schreiben
- [ ] mHM Outputs auf Repository hochladen (oder auf Anfrage?)
- [ ] CAMELS-DE und EDID korrekt zitieren
- [ ] DWD-Lizenz prüfen (Datenverteilung erlaubt?)

---

## 🎨 **FIGURE QUALITY CHECK** ⚠️

### 7. Figure-Format für Publication ⚠️

**Aktuell:** PNG-Files, verschiedene Größen

**Journal Requirements (HESS):**
- Format: TIFF oder EPS (vector preferred)
- Auflösung: 300 DPI minimum für Photos, 600 DPI für Line Art
- Farbmodus: RGB oder CMYK
- Schriftgrößen: Mind. 8pt nach Skalierung

**Aufgabe:**
- [ ] Alle 17 Plots als SVG oder PDF exportieren (vector)
- [ ] Alternativ: PNG mit 600 DPI neu rendern
- [ ] Figure-Sizes konsistent machen (Spaltenbreite anpassen)
- [ ] Fonts prüfen (serifenlos, konsistent)

---

## 📧 **SUBMISSION VORBEREITUNG** ⚠️

### 8. Cover Letter ⚠️

**Aufgabe:**
- [ ] Cover Letter an Editor schreiben
- [ ] Novelty Statement formulieren (Warum dieses Paper?)
- [ ] Suggested Reviewers vorschlagen (3-5 Namen)
- [ ] Opposed Reviewers (optional)

### 9. Supplementary Material ⚠️

**Optionaler Inhalt:**
- [ ] Zusätzliche Plots für alle 5 Catchments (wenn nicht im Haupttext)
- [ ] Code-Snippets für MDI-Berechnung
- [ ] Zusätzliche Tabellen (z.B. monatliche Drought-Statistiken)
- [ ] Sensitivity Analysis (MDI-Gewichtung)

**Aufgabe:**
- [ ] Entscheiden: Was ins Supplement?
- [ ] Supplement als separates PDF erstellen

### 10. Ethics & Conflicts ⚠️

**Aufgabe:**
- [ ] Conflict of Interest Statement schreiben (typisch: "The authors declare no competing interests")
- [ ] Author Contributions Statement (wer hat was gemacht?)
- [ ] Acknowledgements (Funding? Kollegen die geholfen haben?)

---

## 📅 **TIMELINE**

| Meilenstein | Datum | Status |
|-------------|-------|--------|
| Rohfassung vollständig | 2026-03-05 | ✅ Fertig |
| Internes Review (Julian) | 2026-03-05 bis 2026-03-12 | ⏳ Ausstehend |
| Co-Author Review | 2026-03-12 bis 2026-03-19 | ⏳ Ausstehend |
| Figure-Export (high-res) | 2026-03-19 bis 2026-03-26 | ⏳ Ausstehend |
| Final Formatting | 2026-03-26 bis 2026-04-02 | ⏳ Ausstehend |
| Submission | 2026-04-02 | ⏳ Ausstehend |
| First Reviews erwartet | ~2026-06-02 | ⏳ Ausstehend |

---

## 🚀 **NÄCHSTE SCHRITTE (Diese Woche)**

1. **[ ] Manuscript komplett durchlesen** (Abschnitt für Abschnitt)
2. **[ ] Figure-Referenzen konsistent machen**
3. **[ ] Table-Formatierung prüfen**
4. **[ ] Co-Authors kontaktieren**
5. **[ ] Target Journal festlegen**

---

## 📞 **KONTAKT FÜR RÜCKFRAGEN**

- **Helferchen** (Research Assistant): Über Telegram verfügbar
- **Codex** (Implementation Partner): Für Code/Data-Fragen

---

**Last Updated:** 2026-03-05  
**Next Review:** Nach Julian's erstem Durchlesen des Manuscripts
