"""
Modern Hydrograph Visualization Research & Design
Best Practices for Hydrological Dashboards (2024-2025)

Based on: AGU Publications, HESS, Nature Water, USGS Water Dashboard, 
         European Drought Observatory, and modern data viz principles.
"""

# =============================================================================
# MODERN HYDROGRAPH DESIGN PRINCIPLES (2024-2025)
# =============================================================================

## 1. VISUAL HIERARCHY & CLARITY

### Key Principles:
- **Primary focus**: Observed discharge (Qobs) as solid, bold line
- **Secondary**: Simulated discharge (Qsim) as dashed/thinner line
- **Context**: Drought/flood periods as subtle background shading
- **Avoid**: Chart junk, excessive gridlines, competing colors

### Color Palette (Colorblind-Friendly):
```python
# Primary (Observed)
QOBS_COLOR = "#1f77b4"  # Blue (viridis first)
QSIM_COLOR = "#ff7f0e"  # Orange (viridis second)

# Drought/Flood Shading
DROUGHT_COLOR = "rgba(214, 39, 40, 0.15)"   # Red, low opacity
FLOOD_COLOR = "rgba(44, 160, 44, 0.15)"     # Green, low opacity

# Threshold Lines
THRESHOLD_LOW = "#d62728"   # Red for low-flow threshold
THRESHOLD_HIGH = "#2ca02c"  # Green for high-flow threshold

# Background
BACKGROUND = "#ffffff"      # White
GRID_COLOR = "rgba(0, 0, 0, 0.05)"  # Very light gray
```

### Typography:
- **Title**: 14-16px, bold, sans-serif (Inter, Roboto, Open Sans)
- **Axis labels**: 11-12px, regular
- **Tick labels**: 10-11px, regular
- **Annotations**: 10px, italic or regular

---

## 2. INTERACTIVE FEATURES (ESSENTIAL FOR DASHBOARDS)

### Must-Have Interactions:
1. **Hover tooltips**: Show exact date, Qobs, Qsim, difference
2. **Zoom/Pan**: Time range selection (brush tool)
3. **Legend toggle**: Click to show/hide series
4. **Time period presets**: 
   - Last 30 days
   - Last year
   - Custom range
   - Drought events (2018, 2019, 2020)
5. **Linked brushing**: Select time range → update all panels

### Advanced Interactions:
- **Click to annotate**: Mark specific events
- **Compare periods**: Overlay 2018 vs 2019 vs 2020
- **Download selection**: Export visible range as CSV/PNG
- **Shareable URL**: Encode time range in URL params

---

## 3. MULTI-PANEL LAYOUTS (RECOMMENDED)

### Layout A: Standard Hydrograph + Context
```
┌────────────────────────────────────────────┐
│  HYDROGRAPH: Qobs vs Qsim                  │
│  [Time series with drought shading]        │
├────────────────────────────────────────────┤
│  PRECIPITATION (DAILY)                     │
│  [Bar chart, inverted or normal]           │
├────────────────────────────────────────────┤
│  SOIL MOISTURE INDEX (SMI)                 │
│  [Area chart or line with threshold]       │
└────────────────────────────────────────────┘
```

### Layout B: Diagnostic Dashboard
```
┌──────────────────┬──────────────────┐
│  HYDROGRAPH      │  FLOW DURATION   │
│  (Time series)   │  (Exceedance)    │
├──────────────────┼──────────────────┤
│  RESIDUALS       │  METRICS TABLE   │
│  (Qobs - Qsim)   │  (KGE, NSE, etc) │
└──────────────────┴──────────────────┘
```

### Layout C: Event-Focused
```
┌────────────────────────────────────────────┐
│  DROUGHT EVENT TIMELINE                    │
│  [2018-2020 with annotations]              │
├────────────────────────────────────────────┤
│  COMPARISON: 2018 vs 2019 vs 2020          │
│  [Overlaid hydrographs, normalized]        │
├────────────────────────────────────────────┤
│  CUMULATIVE DEFICIT                        │
│  [Running total of Qobs - Qsim]            │
└────────────────────────────────────────────┘
```

---

## 4. ENHANCED VISUAL ENCODINGS

### A. Uncertainty Visualization
```python
# If ensemble or confidence intervals available:
fig.add_trace(
    go.Scatter(
        x=dates,
        y=qsim_upper,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        name='Qsim 95% CI'
    )
)
fig.add_trace(
    go.Scatter(
        x=dates,
        y=qsim_lower,
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 127, 14, 0.2)',
        showlegend=False,
        name='Qsim 95% CI'
    )
)
```

### B. Anomaly Highlighting
```python
# Highlight periods where |Qobs - Qsim| > threshold
anomaly_mask = abs(df['qobs'] - df['qsim']) > threshold
for start, end in find_contiguous_periods(anomaly_mask):
    fig.add_vrect(
        x0=start, x1=end,
        fillcolor="rgba(255, 0, 0, 0.1)",
        layer="below",
        annotation="Model anomaly"
    )
```

### C. Seasonal Background
```python
# Show typical seasonal range as background
fig.add_trace(
    go.Scatter(
        x=dates,
        y=q10_seasonal,  # 10th percentile by DOY
        mode='lines',
        line=dict(width=0),
        showlegend=False
    )
)
fig.add_trace(
    go.Scatter(
        x=dates,
        y=q90_seasonal,  # 90th percentile by DOY
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 100, 200, 0.1)',
        showlegend=False,
        name='Typical range (10-90 pct)'
    )
)
```

---

## 5. ANNOTATION BEST PRACTICES

### Essential Annotations:
1. **Extreme events**: "2018 Drought onset", "Record low flow"
2. **Thresholds**: "Q10 (low-flow threshold)", "Q90 (high-flow)"
3. **Statistics**: "KGE = 0.74", "Bias = +5.2%"
4. **Data gaps**: "Missing data" with hatched pattern

### Annotation Style:
- **Position**: Outside plot area when possible (avoid obscuring data)
- **Arrows**: Use for pointing to specific features
- **Background**: Semi-transparent white for readability
- **Font**: Slightly smaller than axis labels (9-10px)

---

## 6. RESPONSIVE DESIGN (MOBILE-FIRST)

### Mobile Layout (< 768px):
- **Single column**: Stack all panels vertically
- **Simplified legend**: Icons only, expand on tap
- **Touch-friendly**: Minimum 44px tap targets
- **Reduced density**: Fewer tick marks, larger fonts

### Tablet (768-1024px):
- **Two columns**: Side-by-side panels
- **Compact legend**: Horizontal below plot

### Desktop (> 1024px):
- **Full layout**: Multi-panel grid
- **Detailed legend**: Right sidebar or overlay

---

## 7. ACCESSIBILITY (WCAG 2.1 AA)

### Color Contrast:
- **Text**: Minimum 4.5:1 contrast ratio
- **Data lines**: Minimum 3:1 against background
- **Don't rely on color alone**: Use patterns, labels, shapes

### Screen Reader Support:
- **Alt text**: Describe overall pattern and key findings
- **Data table**: Provide downloadable CSV
- **ARIA labels**: For interactive elements

### Colorblind Palettes:
```python
# Okabe-Ito (colorblind-safe)
COLORS = [
    "#E69F00",  # Orange
    "#56B4E9",  # Sky Blue
    "#009E73",  # Bluish Green
    "#D55E00",  # Vermilion
    "#CC79A7",  # Reddish Purple
    "#0072B2",  # Blue
    "#F0E442",  # Yellow
]
```

---

## 8. PERFORMANCE OPTIMIZATION

### For Large Datasets (> 10k points):
1. **Downsampling**: LTTB (Largest-Triangle-Three-Buckets) algorithm
2. **Level of Detail (LOD)**: Show aggregated data when zoomed out
3. **Lazy loading**: Load data on demand
4. **WebGL rendering**: Use Plotly WebGL for > 5k points

### Example (Plotly):
```python
# Enable WebGL for large datasets
fig = go.Figure()
fig.add_trace(
    go.Scattergl(  # WebGL version
        x=dates,
        y=qobs,
        mode='lines'
    )
)
```

---

## 9. EXAMPLE IMPLEMENTATION (PLOTLY)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_modern_hydrograph(df, title="Hydrograph"):
    """
    Modern hydrograph with best practices.
    """
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=(
            "Discharge [m³/s]",
            "Precipitation [mm/day]",
            "Soil Moisture Index [-]"
        )
    )
    
    # Row 1: Hydrograph
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['qobs'],
            name='Qobs (CAMELS-DE)',
            line=dict(color='#1f77b4', width=2.5),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Qobs: %{y:.2f} m³/s<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['qsim'],
            name='Qsim (mHM 5.13.2)',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Qsim: %{y:.2f} m³/s<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Drought shading
    drought_mask = df['smi'] < 20
    # ... (add drought rectangles)
    
    # Row 2: Precipitation
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['precip'],
            name='Precipitation',
            marker_color='#2ca02c',
            opacity=0.7,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Precip: %{y:.1f} mm<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Row 3: SMI
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['smi'],
            name='SMI',
            line=dict(color='#9467bd', width=2),
            fill='tozeroy',
            fillcolor='rgba(148, 103, 189, 0.2)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>SMI: %{y:.1f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Threshold line
    fig.add_hline(
        y=20, line_dash='dash', line_color='#d62728',
        annotation_text='Drought threshold',
        row=3, col=1
    )
    
    # Layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, weight='bold')
        ),
        height=700,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=60, r=40, t=80, b=40)
    )
    
    # Axis styling
    fig.update_xaxes(
        tickformat='%Y-%m',
        ticklabelmode='period',
        showgrid=True,
        gridcolor='rgba(0, 0, 0, 0.05)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(0, 0, 0, 0.05)',
        zeroline=True,
        zerolinecolor='rgba(0, 0, 0, 0.1)'
    )
    
    return fig
```

---

## 10. INSPIRATION & REFERENCES

### Leading Examples:
1. **USGS Water Dashboard**: https://dashboard.waterdata.usgs.gov/
   - Clean design, excellent use of color
   - Multi-panel layouts with linked brushing
   
2. **European Drought Observatory (EDO)**: https://edo.jrc.ec.europa.eu/
   - Good use of maps + time series
   - Drought indicator comparison

3. **UK Centre for Ecology & Hydrology**: https://nrfa.ceh.ac.uk/
   - Excellent hydrograph visualizations
   - Contextual information (rainfall, groundwater)

4. **BfG (Germany) - ELWAS**: https://elwasim.bafg.de/
   - Rhine river discharge monitoring
   - Historical context and thresholds

### Key Papers:
- **Kelleher et al. (2020)**: "Improving hydrologic model diagnostics"
- **Addor et al. (2018)**: "CAMELS catchment attributes"
- **Gupta et al. (2009)**: "KGE decomposition" (visualization implications)

---

## 11. CHECKLIST FOR HYDROGRAPHICAL DASHBOARD

### Visual Design:
- [ ] Colorblind-safe palette
- [ ] Clear visual hierarchy (Qobs > Qsim > context)
- [ ] Minimal gridlines and chart junk
- [ ] Readable fonts (11px minimum)
- [ ] Consistent spacing and alignment

### Interactivity:
- [ ] Hover tooltips with exact values
- [ ] Zoom/pan functionality
- [ ] Time period presets
- [ ] Legend toggle
- [ ] Download options (CSV, PNG)

### Context:
- [ ] Drought/flood threshold lines
- [ ] Background shading for events
- [ ] Precipitation or SM context panel
- [ ] Model performance metrics visible
- [ ] Data source attribution

### Accessibility:
- [ ] Color contrast ≥ 4.5:1
- [ ] Not color-only encoding
- [ ] Screen reader compatible
- [ ] Keyboard navigation
- [ ] Mobile responsive

### Performance:
- [ ] < 3 second load time
- [ ] Smooth pan/zoom (60 fps)
- [ ] Progressive loading for large datasets
- [ ] Efficient data formats (Parquet, Arrow)

---

## 12. RECOMMENDED IMPROVEMENTS FOR CHEMNITZ2 DASHBOARD

### Immediate (Low Effort):
1. **Improve hover tooltips**: Show date, Qobs, Qsim, difference
2. **Add precipitation bar chart** below hydrograph
3. **Colorblind-safe palette** (use Okabe-Ito or viridis)
4. **Threshold annotations**: Q10, Q90 lines with labels
5. **Metrics in title**: "KGE = 0.74 | NSE = 0.61"

### Short-term (Medium Effort):
6. **Multi-panel layout**: Add SMI or precipitation context
7. **Time period presets**: "2018 Drought", "Last Year", "Full Record"
8. **Download visible range**: Export current view as CSV/PNG
9. **Event annotations**: Mark 2018 drought onset, peak, recovery
10. **Responsive design**: Mobile-friendly layout

### Long-term (High Effort):
11. **Linked brushing**: Select time range → update all plots
12. **Compare mode**: Overlay multiple years
13. **Uncertainty bands**: If ensemble available
14. **Seasonal context**: Show typical range (10-90 percentile)
15. **Shareable URLs**: Encode view state in URL params

---

**Author**: Helferchen (Research Assistant)  
**Date**: 2026-03-10  
**Version**: 1.0  
**Based on**: AGU/HESS best practices, modern data viz principles
