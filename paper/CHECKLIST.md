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
| Abstract | ✅ Fertig | ~340 | `draft_v1/01_abstract.md` | ✅ |
| Introduction | ✅ Fertig + Literatur | ~1.400 | `draft_v1/02_introduction.md` | ✅ |
| Methods | ✅ Fertig | ~1.850 | `draft_v1/03_methods.md` | ✅ |
| Results | ✅ Fertig | ~2.800 | `draft_v1/04_results.md` | ✅ |
| Discussion | ✅ Fertig + Literatur | ~3.000 | `draft_v1/05_discussion.md` | ✅ |
| Conclusions | ✅ Fertig | ~980 | `draft_v1/06_conclusions.md` | ✅ |
| References | ✅ Fertig | ~30 Papers | `draft_v1/08_references.md` | ✅ |

**Gesamt:** ~10.400 Wörter (Target: ~8.000 für HESS) ✅

**Literatur-Updates (2026-03-09):**
- ✅ Introduction: Zhang et al. (2022), Liu et al. (2023), Tijdeman et al. (2020), Saha et al. (2021)
- ✅ Discussion: Tijdeman, Li, Noguera, Zhang, Stagge, Wu, Barker, Liu, Otkin
- ✅ References: Alle 30 Papers vollständig

---

## 🔧 **OFFENE PUNKTE (Priorität: HOCH)**

### 1. Figure-Referenzen prüfen ✅ ERLEDIGT

**Status:** Figure-Captions erstellt, Mapping vollständig.

**Figure Mapping (11 Hauptfiguren + 6 Supplement):**
- Figure 1 → `01_drought_timeseries.png` — Timeseries of SPI/SPEI/SMI (1991-2020)
- Figure 2 → `02_heatmap_smi.png` — Interannual SMI heatmap
- Figure 3 → `03_heatmap_recharge.png` — Recharge deficit heatmap
- Figure 4 → `04_heatmap_discharge.png` — Streamflow deficit heatmap
- Figure 5 → `05_discharge_analysis.png` — Qobs vs Qsim (KGE, NSE)
- Figure 6 → `06_correlation_matrix.png` — Compartment coupling
- Figure 7 → `07_drought_duration.png` — Event persistence
- Figure 8 → `08_seasonal_boxplots.png` — Monthly distributions
- Figure 9 → `09_lag_correlation.png` — Cross-correlations
- Figure 10 → `10_matrix_drought_index.png` — Integrated MDI
- Figure 11 → `11_discharge_metrics_timeseries.png` — Discharge metrics

**Supplement (A-F):**
- Figure A → `advanced/A_drought_propagation.png`
- Figure B → `advanced/B_event_duration_survival.png`
- Figure C → `advanced/C_interannual_variability.png`
- Figure D → `advanced/D_spatial_comparison.png`
- Figure E → `advanced/E_index_comparison_taylor.png`
- Figure F → `advanced/F_drought_onset_analysis.png`

**Entscheidung:**
- ✅ Hauptfiguren: 1-11 (im Haupttext)
- ✅ Supplement: A-F (online supplement)

**Nächste Schritte:**
- [ ] Figure-Captions als separate Datei exportieren (`figure_captions.md`)
- [ ] Plots als SVG/PDF exportieren (vector, 600 DPI)

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
