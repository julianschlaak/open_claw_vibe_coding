# Context Memory - Project Rules
# Domain: OpenClaw Vibe Coding
# Project: Hydrological Drought Analysis

## Active Project Patterns

[PROJ-001] Flat Directory Structure
Rule: plots/<catchment>/ (no normal/advanced/legacy subdirs)
Source: Pipeline refactoring 2026-03-02
Status: ACTIVE

[PROJ-002] Seasonal Percentiles
Rule: SMI uses calendar-based percentiles (month-to-month), not global ranking
Source: Drought analysis fix 2026-03-02
Status: ACTIVE

[PROJ-003] Volumetric Soil Moisture
Rule: SWC / soil_depth = m³/m³ (not raw mm)
Source: Soil moisture fix 2026-03-02
Status: ACTIVE

[PROJ-004] Bridge Communication
Rule: Use ops/jobs/ for Codex delegation when tools fail
Source: Bridge implementation 2026-03-02
Status: ACTIVE
