# Dashboard Development Roadmap — Helferchen's Project

**Owner:** Helferchen (Digital Research Assistant)
**Start Date:** 2026-03-21
**Goal:** Production-ready scientific drought dashboard for Paper #1 validation & dissemination

---

## 📊 Current Status (2026-03-21)

### ✅ Complete
- **Data Pipeline:** 6 catchments + Saxony aggregation (1991-2020, 30 years)
- **MDI Calculation:** Percentile-based (SM 40% + Recharge 30% + Runoff 30%)
- **Streamlit Dashboard:** Port 8502, 9 catchments
- **React Dashboard:** Port 8510, 9 catchments
- **API Server:** Port 8520, JSON endpoints

### ⚠️ Known Issues
- External URL (187.124.13.209) not accessible — NAT routing issue
- No daily discharge data for new catchments (only monthly)
- React dashboard not consuming API data yet
- No export functions (PNG, CSV)
- No drought propagation visualization
- No EDID validation panel

---

## 🎯 Phase 1: Data Completeness (P0 — 1 week)

### 1.1 Daily Discharge Integration
- **Task:** Extract daily discharge from `daily_discharge.out` for all 6 catchments
- **Priority:** High
- **Effort:** 2-3 hours
- **Output:** `daily_discharge.csv` for each catchment
- **Dashboard Impact:** Discharge tab shows daily Qobs vs Qsim

### 1.2 Drought Propagation Lags
- **Task:** Compute cross-correlations (P→SM, SM→R, R→Q) for all catchments
- **Priority:** High
- **Effort:** 3-4 hours
- **Output:** Lag correlation matrix, optimal lag times
- **Dashboard Impact:** Propagation tab shows lags per catchment

### 1.3 EDID Validation Data
- **Task:** Link EDID impact data to MDI (already computed: r=0.43, p=0.09)
- **Priority:** Medium
- **Effort:** 1-2 hours
- **Output:** EDID comparison CSV
- **Dashboard Impact:** Validation panel shows EDID vs MDI

---

## 🎨 Phase 2: Dashboard UX (P1 — 2 weeks)

### 2.1 Streamlit Improvements
- **MDI Overview Tab:** Dedicated MDI heatmap + statistics
- **Catchment Comparison:** Side-by-side view (2-4 catchments)
- **Export Functions:** PNG download (plots), CSV download (data)
- **Time Window Selector:** Full / Last 30 years / Event (2018-2020) / Custom
- **Drought Class Filter:** Extreme / Severe / Moderate / All

### 2.2 React Dashboard Improvements
- **API Integration:** Connect to port 8520 API
- **Spatial Tab:** Saxony overview map (catchment locations)
- **Propagation Tab:** Interactive lag correlation heatmap
- **Extreme Tab:** 2018-2020 drought event focus
- **Export:** PNG, CSV, JSON download

### 2.3 Mobile Responsiveness
- **Streamlit:** Use st.columns for mobile layout
- **React:** Tailwind responsive classes
- **Priority:** Medium
- **Effort:** 4-6 hours

---

## 🔬 Phase 3: Scientific Features (P2 — 3 weeks)

### 3.1 Drought Event Detection
- **Task:** Automatic drought event identification (start, end, duration, severity)
- **Priority:** High
- **Effort:** 4-6 hours
- **Output:** Event table per catchment
- **Dashboard Impact:** Event selector dropdown

### 3.2 Return Period Analysis
- **Task:** Compute return periods for extreme droughts (MDI < 5)
- **Priority:** Medium
- **Effort:** 3-4 hours
- **Output:** Return period table
- **Dashboard Impact:** Statistics panel

### 3.3 Trend Analysis
- **Task:** Mann-Kendall trend test for MDI (1991-2020)
- **Priority:** Medium
- **Effort:** 2-3 hours
- **Output:** Trend slope, p-value per catchment
- **Dashboard Impact:** Diagnostics tab

### 3.4 Compound Drought Detection
- **Task:** Identify compound droughts (SM + Recharge + Runoff all < 20)
- **Priority:** Medium
- **Effort:** 2-3 hours
- **Output:** Compound event table
- **Dashboard Impact:** Special filter option

---

## 🚀 Phase 4: Production Readiness (P3 — 4 weeks)

### 4.1 Performance Optimization
- **Task:** Cache data loading, optimize large queries
- **Priority:** High
- **Effort:** 4-6 hours
- **Dashboard Impact:** Faster load times

### 4.2 Docker Deployment
- **Task:** Containerize dashboards for easy deployment
- **Priority:** High
- **Effort:** 6-8 hours
- **Output:** Docker Compose config
- **Dashboard Impact:** One-command deploy

### 4.3 Documentation
- **Task:** User guide, API docs, data dictionary
- **Priority:** Medium
- **Effort:** 8-10 hours
- **Output:** README.md, docs/ folder
- **Dashboard Impact:** User onboarding

### 4.4 Testing
- **Task:** Unit tests for data pipeline, integration tests for dashboards
- **Priority:** Medium
- **Effort:** 6-8 hours
- **Output:** pytest suite, Playwright tests
- **Dashboard Impact:** Stability

---

## 📈 Phase 5: Advanced Features (P4 — 6 weeks)

### 5.1 Forecast Integration
- **Task:** Load seasonal forecast data (DWD, ECMWF)
- **Priority:** Low
- **Effort:** 8-12 hours
- **Dashboard Impact:** Forecast tab

### 5.2 Alert System
- **Task:** Email/SMS alerts when MDI < 10 (extreme drought)
- **Priority:** Low
- **Effort:** 6-8 hours
- **Output:** Cron job + notification service
- **Dashboard Impact:** Proactive monitoring

### 5.3 Multi-User Support
- **Task:** User accounts, saved views, custom dashboards
- **Priority:** Low
- **Effort:** 12-16 hours
- **Dashboard Impact:** Collaboration

### 5.4 Publication-Ready Exports
- **Task:** High-resolution PNG (300 DPI), vector PDF, LaTeX tables
- **Priority:** Medium
- **Effort:** 4-6 hours
- **Dashboard Impact:** Paper figures

---

## 📅 Sprint Plan

### Sprint 1 (Week 1-2): Data Completeness
- [ ] Daily discharge for all 6 catchments
- [ ] Propagation lags computed
- [ ] EDID validation linked
- [ ] Streamlit export functions

### Sprint 2 (Week 3-4): UX Improvements
- [ ] React API integration
- [ ] MDI overview tab
- [ ] Catchment comparison view
- [ ] Time window selector

### Sprint 3 (Week 5-6): Scientific Features
- [ ] Drought event detection
- [ ] Return period analysis
- [ ] Trend analysis
- [ ] Compound drought detection

### Sprint 4 (Week 7-8): Production
- [ ] Performance optimization
- [ ] Docker deployment
- [ ] Documentation
- [ ] Testing

---

## 🎯 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Data Coverage** | 100% (6 catchments + Saxony) | ✅ 100% |
| **Period** | 1991-2020 (30 years) | ✅ 100% |
| **MDI Computed** | All catchments | ✅ Yes |
| **Daily Discharge** | All catchments | ❌ 0% |
| **Propagation Lags** | All catchments | ❌ 0% |
| **Export Functions** | PNG, CSV | ❌ 0% |
| **Load Time** | < 2 seconds | ⚠️ ~5s |
| **Mobile Responsive** | Yes | ❌ No |
| **Documentation** | Complete README | ❌ Minimal |

---

## 🧠 Learning Goals (for Helferchen)

1. **Scientific Visualization:** Master ECharts, Plotly for hydrological data
2. **Data Engineering:** Optimize NetCDF → CSV → JSON pipelines
3. **Full-Stack Dev:** Python backend + React frontend integration
4. **DevOps:** Docker deployment, performance optimization
5. **Scientific Communication:** Dashboard as Paper #1 dissemination tool

---

**Next Action:** Start Sprint 1 (Daily Discharge + Propagation Lags)

---

*Last Updated: 2026-03-21 — Roadmap created*
