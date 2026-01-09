# Forecast Dashboard Logic Reference

Pure business logic for BSC forecast analysis. No code.

---

## Overview

**Purpose:** Analyze BSC Research forecasts and compare with consensus
**Key Metrics:** Target Price, Upside, PE Forward, EPS Growth, Rating
**Data Source:** `DATA/processed/forecast/`

---

## Header Metrics

| Metric | Source | Display |
|--------|--------|---------|
| Total Stocks | Count of BSC universe | Number |
| Strong Buy | Count rating="STRONG BUY" | Number |
| Avg Upside | Mean of upside_potential | +X.X% |
| Median PE 25F | Median of pe_fwd_2025 | X.Xx |

---

## Tab 0: BSC Universal

### Unified Stock Table

| Column | Source | Format |
|--------|--------|--------|
| Ticker | `symbol` | Link |
| Sector | `sector` | Text |
| Rating | `rating` | Badge (5 colors) |
| Target Price | `target_price` | VND |
| Upside | `upside_potential` | +X.X% (colored) |
| PE 25F | `pe_fwd_2025` | X.Xx |
| PE 26F | `pe_fwd_2026` | X.Xx |
| EPS 25F | `eps_2025` | VND |
| EPS 26F | `eps_2026` | VND |
| Market Cap | `market_cap` | B/T |

### Filter Options
- Sector dropdown
- Rating multiselect
- Ticker search
- Sort by any column

---

## Tab 1: Sector

### Sector Valuation Table

| Column | Source | Format |
|--------|--------|--------|
| Sector | Group name | Text |
| Ticker Count | Count per sector | Number |
| PE 25F | Median of sector | X.Xx |
| PE 26F | Median of sector | X.Xx |
| PB 25F | Median of sector | X.Xx |
| Avg Upside | Mean of sector | +X.X% |

### Valuation Matrix Chart
- Distribution by sector
- Current vs historical comparison

---

## Tab 2: Achievement

### Achievement Tracking

| Metric | Formula | Color Coding |
|--------|---------|--------------|
| YTD Achievement | Current NPATMI / Target NPATMI | Green >75%, Yellow 50-75%, Red <50% |
| EPS Achievement | Actual EPS / Forecast EPS | Same scale |

### Achievement Cards
- On Track (>75%)
- Behind (50-75%)
- At Risk (<50%)

---

## Tab 3: Consensus (BSC vs Market)

### Comparison Table

| Column | BSC Source | Consensus Source |
|--------|------------|------------------|
| NPATMI 2025F | `bsc.npatmi_2025f` | Average of VCI, HCM, SSI |
| NPATMI 2026F | `bsc.npatmi_2026f` | Average of VCI, HCM, SSI |
| Deviation | (Consensus - BSC) / BSC | Colored |

### Insight Categories

| Insight | Deviation | Meaning |
|---------|-----------|---------|
| Strong Bullish | ≤ -15% | BSC much higher than consensus |
| Bullish Gap | -15% to -5% | BSC moderately higher |
| Aligned | -5% to +5% | BSC ≈ consensus |
| Bearish Gap | +5% to +15% | BSC moderately lower |
| Strong Bearish | ≥ +15% | BSC much lower |
| High Variance | Spread > 30% | Sources disagree significantly |

---

## Rating Color Scheme

| Rating | Color | Hex |
|--------|-------|-----|
| STRONG BUY | Teal | #00C9AD |
| BUY | Green | #22C55E |
| HOLD | Gold | #FFC132 |
| SELL | Orange | #F97316 |
| STRONG SELL | Red | #EF4444 |
| N/A | Gray | #94A3B8 |

---

## Valuation Formulas

### PE Forward
```
PE FWD 2025 = Market Cap / NPATMI 2025F
PE FWD 2026 = Market Cap / NPATMI 2026F
```

### PB Forward (Parent Equity)
```
Parent Equity Q4/2024 = Total Equity Q4/2024 - Minority Interest
Equity 2025F = Parent Equity Q4/2024 + NPATMI 2025F
Equity 2026F = Equity 2025F + NPATMI 2026F

PB FWD 2025 = Market Cap / Equity 2025F
PB FWD 2026 = Market Cap / Equity 2026F
```

**IMPORTANT:** PB FWD uses Q4/2024 (year-end 2024) equity, NOT TTM (latest quarter).

### Book Value Per Share
```
BVPS 2025F = Equity 2025F / Shares Outstanding
BVPS 2026F = Equity 2026F / Shares Outstanding
```

### Minority Interest Codes
| Entity Type | Code |
|-------------|------|
| Company | CBS_429 |
| Bank | BBS_700 |
| Security | SBS_418 |
| Insurance | IBS_4214 |

---

## Data Flow

```
1. BSC Excel → bsc.json → bsc_individual.parquet
2. VCI API → vci.json → unified.parquet
3. HCM/SSI PDF → Extract → hcm.json/ssi.json → unified.parquet
4. Compare → BSC vs Consensus insights
```

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/forecast/forecast_dashboard.py` |
| BSC Tab | `WEBAPP/pages/forecast/tabs/bsc_universal_tab.py` |
| Consensus Tab | `WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py` |
| Service | `WEBAPP/services/forecast_service.py` |
| Builder | `PROCESSORS/forecast/unified/build_unified.py` |
| Source Data | `DATA/processed/forecast/sources/` |
| Output | `DATA/processed/forecast/unified.parquet` |
