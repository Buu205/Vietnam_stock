# Sector Dashboard Logic Reference

Pure business logic for sector valuation analysis. No code.

---

## Overview

**Purpose:** Compare sector valuations (PE, PB, PS, EV/EBITDA) with statistical analysis
**Key Features:** Distribution candlesticks, statistical bands, z-scores, percentiles
**Data Source:** `DATA/processed/valuation/`

---

## Tab 0: VN-Index Analysis

### 3 Index Variants

| Index | Scope | Description |
|-------|-------|-------------|
| VNINDEX | Full index | All listed stocks |
| VNINDEX_EXCLUDE | Filtered | Excludes banks with PE<0 |
| BSC_INDEX | BSC Universe | 92 stocks covered by BSC |

### Metrics Bar (Compact)

| Metric | Source | Format |
|--------|--------|--------|
| PE/PB VNINDEX | Latest row | x.x format |
| PE/PB EXCLUDE | Latest row | x.x format |
| PE FWD 2025/2026 | BSC_INDEX | x.x format |

### Charts

1. **3-Index Comparison Line Chart**
   - X: Date (d/m/Y format)
   - Y: Selected metric (PE or PB)
   - Legend: VNIndex, VNIndex (Exclude), BSC Index

2. **Distribution Candlestick**
   - Body: P25-P75
   - Whiskers: Min-Max
   - Dot: Current value (5-level color)

3. **Individual Index Detail**
   - Line with statistical bands (±1σ, ±2σ)
   - Histogram distribution

---

## Tab 1: Valuation

### Sub-Tab: Sector Comparison

**Candlestick Distribution Chart**
- Each sector as candlestick
- Body: P25-P75 (interquartile range)
- Whiskers: Min-Max (filtered outliers)
- Current value dot: 5-level color coding

### Sub-Tab: Sector Individual

**Line Chart with Statistical Bands**
- Mean line
- ±1σ bands (68% confidence)
- ±2σ bands (95% confidence)
- Current value marker

### Sub-Tab: Stock Comparison

Same as sector but for stocks within selected sector.

### Sub-Tab: Stock Individual

Same as sector individual but for single stock.

---

## Valuation Status Levels

| Level | Percentile | Color | Label |
|-------|------------|-------|-------|
| Very Cheap | 0-20% | #10B981 | ● Very Cheap |
| Cheap | 20-40% | #A7F3D0 | ● Cheap |
| Fair | 40-60% | #FCD34D | ● Fair |
| Expensive | 60-80% | #FBBF24 | ● Expensive |
| Very Expensive | 80-100% | #EF4444 | ● Very Expensive |

---

## Outlier Filtering

| Metric | Min | Max |
|--------|-----|-----|
| PE | 0 | 100 |
| PB | 0 | 10 |
| PS | 0 | 20 |
| EV/EBITDA | 0 | 50 |

---

## Statistical Calculations

### Z-Score
```
z = (current - mean) / std
```

### Percentile
```
percentile = (count ≤ current) / total × 100
```

### Status Assessment

| Z-Score | Assessment |
|---------|------------|
| < -2σ | Very Cheap |
| -2σ to -1σ | Cheap |
| -1σ to +1σ | Fair |
| +1σ to +2σ | Expensive |
| > +2σ | Very Expensive |

---

## Color Reference

| State | Hex | Usage |
|-------|-----|-------|
| Primary | #8B5CF6 | VNIndex charts |
| Secondary | #06B6D4 | VNIndex Exclude |
| Tertiary | #F59E0B | BSC Index |
| Positive | #10B981 | Cheap valuation |
| Negative | #EF4444 | Expensive valuation |

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/sector/sector_dashboard.py` |
| Service | `WEBAPP/services/sector_service.py` |
| Valuation Config | `WEBAPP/core/valuation_config.py` |
| Chart Components | `WEBAPP/components/charts/valuation_charts.py` |
| Data | `DATA/processed/valuation/vnindex/`, `DATA/processed/valuation/sector/` |
