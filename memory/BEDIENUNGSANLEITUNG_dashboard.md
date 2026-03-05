# 🌍 Dürremonitor Sachsen — Kurzanleitung

**URL:** http://187.124.13.209:8502/

---

## 📍 WAS SIE HIER SEHEN

Das Dashboard zeigt **Bodenfeuchte und Dürre-Zustände für Sachsen** in Echtzeit. Wählen Sie einen Zeitraum und klicken Sie auf die Karte für detaillierte Informationen.

---

## 🎯 SCHNELLSTART (3 Schritte)

### 1️⃣ Zeitraum wählen (Sidebar links)

- **Jahr:** 2005–2020 verschieben
- **Monat:** 1–12 verschieben
- **Pfeile:** ◀️ ▶️ für Tag vor/zurück

### 2️⃣ Tab auswählen (oben)

| Tab | Was es zeigt |
|-----|--------------|
| **🌱 %nFK** | Pflanzenverfügbares Wasser (0-100%) |
| **💧 Vol. Bodenfeuchte** | Absoluter Wassergehalt (Vol.%) |
| **📊 SMI** | Dürre im Vergleich zur Geschichte (0-100) |
| **🎯 Multi-Index** | Alle Indizes kombiniert (Radar-Plot) |
| **📚 Wissenschaft** | Quellen & Methodik |

### 3️⃣ Auf Karte klicken

- **Klick auf eine Zelle** → Zeigt detaillierte Werte
- **Rechteck ziehen** (Sidebar) → Mehrere Zellen auswählen
- **Zeitreihe unten** → Verlauf für ausgewählte Zelle

---

## 🗺️ KARTE BEDIENEN

| Aktion | Was passiert |
|--------|--------------|
| **Klick auf Zelle** | Wert + Datum wird angezeigt |
| **Rechteck zeichnen** | Mehrere Zellen auswählen |
| **Scrollen** | Rein/Raus zoomen |
| **Ziehen** | Karte verschieben |

**Farben:**
- 🔴 **Rot** = Trocken/Dürre
- 🟡 **Gelb** = Warnung/Mäßig
- 🟢 **Grün** = Normal/Feucht
- 🔵 **Blau** = Sehr feucht

---

## 📊 ZEITREIHE (unter der Karte)

Zeigt den **Verlauf für die ausgewählte Zelle**:

- **X-Achse:** Zeit (2005–2020)
- **Y-Achse:** Index-Wert (0–100)
- **Blaue Markierung:** Aktuell gewählter Monat
- **Linie:** Wie hat sich der Wert entwickelt?

**Ohne Auswahl:** Zeigt Sachsen-Durchschnitt

---

## 💾 EXPORT (Sidebar unten)

### CSV Download

1. **Rechteck auf Karte zeichnen** (mehrere Zellen)
2. **"CSV herunterladen"** klicken
3. **Datei enthält:**
   - Alle Werte für ausgewählte Zellen
   - Zeitreihe (2005–2020)
   - Flächenmittel (`area_mean`)

### Format

```csv
date,lat,lon,smi,nfk,mdi,area_mean
2018-08-01,51.05,13.74,12.5,35.2,28.4,31.2
...
```

---

## 📈 WERTE INTERPRETIEREN

### %nFK (Tab 1)

| Wert | Bedeutung |
|------|-----------|
| < 30% | 🔴 Trockenstress (Pflanzen leiden) |
| 30–50% | 🟠 Warnung |
| 50–70% | 🟢 Optimal |
| > 70% | 🔵 Feucht |

### SMI (Tab 3)

| Wert | Bedeutung |
|------|-----------|
| < 2 | 🔴 Extreme Dürre (1-in-50-Jahre) |
| 2–5 | 🟠 Schwere Dürre |
| 5–10 | 🟡 Mäßige Dürre |
| 10–20 | 🟢 Leichte Dürre |
| > 20 | ⚪ Normal |

### MDI (Tab 4)

| Wert | Bedeutung |
|------|-----------|
| < 20 | 🔴 Alle Kompartimente trocken |
| 20–40 | 🟠 Mehrere trocken |
| 40–60 | 🟡 Einzelne trocken |
| > 60 | 🟢 Unauffällig |

---

## ❓ HÄUFIGE FRAGEN

**Q: Warum sind manche areas grau?**  
A: Keine Daten verfügbar (z.B. Gewässer, Städte).

**Q: Wie aktuell sind die Daten?**  
A: 2005–2020 (30-Jahre Klimareferenz).

**Q: Kann ich eigene Gebiete exportieren?**  
A: Ja! Rechteck auf Karte ziehen → CSV Download.

**Q: Was bedeutet "area_mean"?**  
A: Durchschnittswert aller ausgewählten Zellen.

---

## 📞 KONTAKT

**Autor:** Julian Schlaak  
**Institution:** University of Leipzig, Institute for Geography  
**Email:** [your.email@uni-leipzig.de]

**Zitierung:**
```
Schlaak, J. (2026). Dürremonitor Sachsen [Dashboard]. 
http://187.124.13.209:8502/
```

---

**Viel Erfolg bei der Analyse! 🌍💧**

*Stand: 2026-03-05 | Version 1.0*
