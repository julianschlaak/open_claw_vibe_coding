# Repository Cleanup Plan

**Erstellt:** 2026-03-05  
**Priorität:** Mittel (kann nach Paper-Submission)  
**Geschätzte Zeit:** 30 Minuten  
**Risiko:** Niedrig (mit Backup-Branch)

---

## 🎯 ZIEL

Redundante Strukturen entfernen, Pfade konsolidieren, Repository für langfristige Wartung optimieren.

---

## 📊 AKTUELLE PROBLEME

### 1. Redundante Ordner

```
open_claw_vibe_coding/
├── code/mhm/           ✅ ECHTES mHM (Source + Catchments + Outputs)
├── model/mhm/          ❌ REDUNDANT (nur docs/setup, ~10 MB)
├── dashboard/          ❌ ALT (veraltet)
├── dashboard_saxony/   ✅ NEU (aktiv)
└── dashboard_vnext/    ❌ ALT (veraltet, ~10 MB)
```

### 2. Große Files die nicht gepusht werden sollen

- `code/mhm/venv/` — ~500 MB (Python Virtual Environment)
- `code/mhm/output/*.nc` — Mehrere GB (mHM Daily/Monthly Outputs)
- `code/mhm/catchment_custom/output_*/daily_*.nc` — ~2 GB

### 3. Inkonsistente Pfade

| File | Problem |
|------|---------|
| `analysis/scripts/simple_analysis.py` | Absoluter Pfad (`/data/.openclaw/workspace/...`) |
| `dashboard_saxony/utils/geo_utils.py` | Leading Slash (`/code/mhm/shapes/`) |

---

## 📝 SCHRITT-FÜR-SCHRITT PLAN

### Phase 1: Backup (5 min)

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding

# Backup-Branch erstellen
git checkout main
git checkout -b cleanup-backup-$(date +%Y%m%d)
git push -u origin cleanup-backup-$(date +%Y%m%d)
```

### Phase 2: Analyse (5 min)

```bash
# 1. Alle Pfade finden die "code/mhm" enthalten
grep -r "code/mhm" analysis/ dashboard_saxony/ --include="*.py"

# 2. Große Files identifizieren
find code/mhm -name "*.nc" -size +50M | wc -l

# 3. Ordner-Größen prüfen
du -sh model/mhm/ dashboard/ dashboard_vnext/ code/mhm/venv/
```

### Phase 3: Bereinigung (10 min)

```bash
# 1. Redundante Ordner löschen
rm -rf model/mhm/
rm -rf dashboard/
rm -rf dashboard_vnext/

# 2. Venv löschen (nicht im Repo behalten)
rm -rf code/mhm/venv/

# 3. .gitignore aktualisieren (siehe unten)
```

### Phase 4: Pfade fixen (10 min)

```bash
# 1. Absolute Pfade zu relativen machen (in allen Scripts)
find analysis/scripts/ -name "*.py" -exec sed -i \
  's|/data/.openclaw/workspace/open_claw_vibe_coding/||g' {} \;

# 2. Leading slash in Pfaden entfernen (Dashboard)
sed -i 's|/code/mhm|code/mhm|g' dashboard_saxony/utils/*.py

# 3. Testing
python analysis/scripts/01_load_data.py --catchment test_domain
```

### Phase 5: .gitignore aktualisieren

**Zu `.gitignore` hinzufügen:**

```gitignore
# === mHM Model ===
code/mhm/venv/
code/mhm/output/*.nc
code/mhm/output/*.out
code/mhm/catchment_custom/output_*/daily_*.nc
code/mhm/catchment_custom/output_*/monthly_*.nc
code/mhm/catchments_cloud/output_*/

# === Large Data Files ===
*.nc
*.tif
*.tiff
*.grb
*.grib
*.bin

# === Old Dashboards ===
dashboard/
dashboard_vnext/

# === Python ===
__pycache__/
*.pyc
*.pyo
*.egg-info/

# === IDE ===
.vscode/
.idea/
*.swp
*.swo
```

### Phase 6: Commit & Push

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding

git status
git add -A

git commit -m "Cleanup: Remove redundant folders, fix paths, update .gitignore

REMOVED:
- model/mhm/ (empty, redundant with code/mhm/)
- dashboard/ (replaced by dashboard_saxony/)
- dashboard_vnext/ (replaced by dashboard_saxony/)
- code/mhm/venv/ (large Python venv, not needed in repo)

FIXED:
- Convert absolute paths to relative in analysis/scripts/
- Remove leading slash in dashboard_saxony/utils/ paths
- Update .gitignore to exclude *.nc, venv/, old outputs

RESULT:
- Repository size reduced by ~525 MB
- All paths now relative and portable
- Clean structure for long-term maintenance

Dashboard: http://187.124.13.209:8502/"

# Push zu aktuellem Branch
git push origin HEAD
```

---

## 📁 NEUE STRUKTUR (nach Cleanup)

```
open_claw_vibe_coding/
├── .gitignore                 ✅ Updated
├── README.md                  ✅ Updated (neue Struktur)
│
├── code/mhm/                  ✅ mHM Model (Source + Setups)
│   ├── src/                   (Source Code)
│   ├── catchment_custom/      (30-year simulations)
│   ├── test_domain/           (Test runs)
│   ├── shapes/Saxony/         (Administrative boundaries)
│   └── ... (mHM Code)
│
├── dashboard_saxony/          ✅ Active Dashboard
│   ├── app.py
│   ├── utils/
│   ├── data/
│   └── assets/
│
├── analysis/                  ✅ Analysis Pipeline
│   ├── scripts/               (01-05 + helpers)
│   ├── plots/                 (85 PNGs)
│   └── results/               (Parquet/CSV)
│
├── paper/                     ✅ PhD Paper #1
│   ├── draft_v1/              (7 sections)
│   └── CHECKLIST.md
│
├── memory/                    ✅ Documentation
├── research/                  ✅ Literature
└── ops/                       ✅ Operations
    └── CLEANUP_PLAN.md        ✅ THIS FILE
```

---

## ⚠️ RISIKEN & LÖSUNGEN

| Risiko | Lösung |
|--------|--------|
| Pfade in Scripts brechen | Alle Scripts mit `grep` prüfen |
| Dashboard verliert Shapefile | Pfad in `geo_utils.py` testen |
| User gewohnt an alte Pfade | Symlinks für 1 Woche erstellen |
| Große Files bereits in History | `git filter-branch` wenn nötig |

---

## ✅ CHECKLISTE (nach Abschluss)

- [ ] Backup-Branch erstellt
- [ ] `model/mhm/` gelöscht
- [ ] `dashboard/` gelöscht
- [ ] `dashboard_vnext/` gelöscht
- [ ] `code/mhm/venv/` gelöscht
- [ ] `.gitignore` aktualisiert
- [ ] Alle Pfade in Scripts getestet
- [ ] Dashboard startet erfolgreich
- [ ] Commit & Push erfolgreich
- [ ] README.md aktualisiert

---

## 📞 KONTAKT

Bei Fragen: Helferchen (Telegram) oder Codex (Implementation)

---

**Status:** Bereit zur Umsetzung  
**Nächster Schritt:** Warte auf Julian's Entscheidung
