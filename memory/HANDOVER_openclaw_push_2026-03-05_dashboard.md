# HANDOVER an OpenClaw – Dashboard Sachsen (2026-03-05)

Bitte dieses Update übernehmen und **Repository committen + pushen**.

## Status
Dashboard wurde umfassend überarbeitet und stabilisiert. App startet, Syntaxchecks laufen durch.

## Wichtige umgesetzte Änderungen

### 1) Karten-/Rasterlogik
- Sachsen-Grenze aus offiziellem Shapefile eingebunden.
- Raster wird an Sachsen-Grenze geclippt.
- Zusätzlich vollständiges regelmäßiges Sachsen-Raster erzeugt und Werte per nächster Modellzelle gemappt, um Lücken im Randbereich zu vermeiden.
- Layer transparenter gemacht, aber sichtbar belassen.

### 2) Interaktion und Layout
- Klick auf Rasterzelle aktualisiert aktive Zelle + Zeitbezug.
- Kartenlayout verbreitert, sodass linke/rechte Hauptspalte sauberer bündig wirken.
- Ansichtsauswahl: Dropdown entfernt, durch durchgehenden Button-Balken ersetzt.

### 3) Statistik-/Info-UX
- Alte 4er-Statboxen entfernt.
- Rechts jetzt kompakte "Aktueller Wert"-Karte + kurze, klassenbasierte Dürreeinschätzung.
- Klassengrenzen-Tabelle wieder eingefügt (unter Karte), zweite Legende unter Diagramm/Radar.

### 4) Exporttool (neu)
- Mehrfachauswahl von Rasterzellen per Draw-Rechteck auf Karte.
- Auswahl-/Exporttool in Sidebar verschoben (unter Datum/Fallback), wie gewünscht.
- CSV-Download: komplette Zeitreihe pro ausgewählter Zelle + Flächenmittel (`area_mean`).
- Aktuelles Flächenmittel der Auswahl wird in Sidebar angezeigt.

### 5) Wissenschaft/Quellen
- Quellenbereich konsolidiert und mit belastbarer Kernliteratur aktualisiert.
- Problematische Alt-Links ersetzt.
- BibTeX-Datei aktualisiert.

## Betroffene Dateien
- dashboard_saxony/app.py
- dashboard_saxony/utils/data_loader.py
- dashboard_saxony/utils/geo_utils.py
- dashboard_saxony/utils/plotting.py
- dashboard_saxony/assets/style.css
- dashboard_saxony/data/references.bib
- memory/research/dashboard_sources_handover_2026-03-05.md

## OpenClaw – bitte jetzt ausführen
1. `cd /data/.openclaw/workspace/open_claw_vibe_coding`
2. `git status`
3. Änderungen prüfen (`git diff`)
4. Commit erstellen (Dashboard-Update)
5. **Push auf Remote** (`git push origin <branch>`)

## Vorschlag Commit-Message
`Dashboard Sachsen: finalize UI/UX, raster selection export, clipping robustness, and scientific/source updates`

