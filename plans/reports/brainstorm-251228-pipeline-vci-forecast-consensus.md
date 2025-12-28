# Brainstorm: Pipeline Status & VCI Forecast Consensus Integration

**Date:** 2025-12-28
**Topic:** Phase 1 Review, Pipeline Status Update, VCI Forecast for Consensus Comparison
**Status:** Complete

---

## Problem Statement

1. **Phase 1 Validity**: Review if Phase 1 architecture is still reasonable given current state
2. **Pipeline Status**: Update daily pipeline status with latest changes
3. **VCI Forecast**: Integrate VCI forecast metadata for consensus comparison with BSC

---

## Current State Analysis

### Pipeline Status (Dec 28, 2025)

**Current Pipeline (6 steps):**
```
1. OHLCV Update → raw/ohlcv/OHLCV_mktcap.parquet
2. Technical Analysis (9 sub-steps) → processed/technical/basic_data.parquet
3. Macro & Commodity → processed/macro_commodity/macro_commodity_unified.parquet
4. Stock Valuation → processed/valuation/{pe,pb,ps,ev_ebitda}/historical/*.parquet
5. Sector Analysis → processed/sector/sector_*.parquet
6. BSC Forecast → processed/forecast/bsc/*.parquet
```

**Data Status:**
| Source | Records | Tickers | Latest | Status |
|--------|---------|---------|--------|--------|
| OHLCV | 1M+ | 458 | 2025-12-16 | ⚠️ Stale |
| Technical | 89,805 | 458 | 2025-12-16 | ⚠️ Stale |
| PE/PB | 789K each | 458 | 2025-12-16 | ⚠️ Stale |
| BSC Forecast | 93 stocks | 93 | 2025-12-28 | ✅ Current |

### VCI Forecast Data

**Available:** `DATA/processed/forecast/VCI/vci_coverage_universe.json` (3653 lines, 83KB)

**Structure (list of 83 tickers):**
```json
{
  "ticker": "ACB",
  "sector": "Banks",
  "rating": "BUY",
  "targetPrice": 33300.0,
  "pe": {"2025F": 6.96, "2026F": 5.93},
  "pb": {"2025F": 1.21, "2026F": 1.00},
  "roe": {"2025F": 0.201, "2026F": 0.208},
  "npatmiGrowth": {"2025F": 0.0587, "2026F": 0.1747},
  "analyst": "Nga Ho",
  "adtvVnd": {"6M": ..., "3M": ..., "1M": ...}
}
```

**Key Fields:**
- Target price, rating, sector
- Forward PE/PB (2025F, 2026F)
- Forward ROE, NPATMI growth
- Analyst name (consensus tracking)

---

## Question 1: Phase 1 Validity

### Current Phase 1 (From CLAUDE.md)

**Phase 0.5** - Path Migration (BLOCKING - 81.4% files using deprecated paths)
**Phase 1** - FA+TA Sector Analysis orchestration layer (NOT STARTED)

### Assessment: Phase 1 NO LONGER REASONABLE

**Problems:**

1. **Phase 1 Already Exists** - Sector analysis orchestration is COMPLETE:
   - `PROCESSORS/sector/sector_processor.py` - Main orchestrator ✅
   - `PROCESSORS/sector/calculators/fa_aggregator.py` - FA aggregation ✅
   - `PROCESSORS/sector/calculators/ta_aggregator.py` - TA aggregation ✅
   - `PROCESSORS/sector/scoring/signal_generator.py` - Signal generation ✅
   - Output files exist in `DATA/processed/sector/` ✅

2. **Technical Analysis Pipeline Already Complete** - 9-step TA system exists:
   - VN-Index Analysis, TA indicators, alerts, money flow, sector breadth, market regime, RS Rating
   - All integrated in `PROCESSORS/pipelines/daily/daily_ta_complete.py` ✅

3. **Path Migration Should Be Phase 1** - This is the actual BLOCKING issue:
   - 35/43 files (81.4%) still use deprecated paths
   - Cannot proceed with new features until paths are canonical

### Recommendation: RENAME Phases

```
OLD Phase 0.5 → NEW Phase 1 (Path Migration - CRITICAL)
OLD Phase 1 → SKIP (Already implemented in sector/ module)
```

**Updated Roadmap:**
- **Phase 1**: Path Migration (35 files to update)
- **Phase 2**: Consensus Comparison System (BSC vs VCI vs others)
- **Phase 3**: Enhanced Forecast Dashboard (multi-source comparison)
- **Phase 4**: Alert System (consensus divergence alerts)

---

## Question 2: Pipeline Status Update

### Recommended Pipeline Additions

**Step 7: Consensus Comparison** (NEW)
```python
# PROCESSORS/pipelines/daily/daily_consensus_update.py

def compare_bsc_vci_forecasts():
    """
    Compare BSC vs VCI forecasts for consensus tracking.
    Highlights:
    - Rating disagreements (BUY vs HOLD)
    - Target price divergence >15%
    - Forward PE/PB differences
    - Analyst attribution
    """
    bsc_df = pd.read_parquet("DATA/processed/forecast/bsc/bsc_individual.parquet")
    vci_df = pd.read_json("DATA/processed/forecast/VCI/vci_coverage_universe.json")

    # Merge on symbol
    merged = bsc_df.merge(vci_df, left_on='symbol', right_on='ticker', how='outer', suffixes=('_bsc', '_vci'))

    # Calculate divergences
    merged['target_price_divergence_pct'] = (
        (merged['target_price_vci'] - merged['target_price_bsc']) / merged['target_price_bsc']
    )
    merged['rating_match'] = merged['rating_bsc'] == merged['rating_vci']
    merged['pe_fwd_2025_diff'] = merged['pe_fwd_2025_bsc'] - merged['pe_2025F']

    # Flag divergences
    divergences = merged[
        (abs(merged['target_price_divergence_pct']) > 0.15) |  # >15% price diff
        (~merged['rating_match'])  # Rating mismatch
    ]

    return merged, divergences
```

**Output:**
```
DATA/processed/forecast/consensus/
├── consensus_comparison.parquet        # All tickers merged
├── consensus_divergences.parquet       # Flagged divergences
└── consensus_summary.json             # Daily summary stats
```

### Updated Master Pipeline

```python
# PROCESSORS/pipelines/run_all_daily_updates.py

PIPELINE_STEPS = [
    ("ohlcv", "OHLCV Data Update", daily_ohlcv_update),
    ("ta", "Technical Analysis", daily_ta_complete),
    ("macro", "Macro & Commodity", daily_macro_commodity),
    ("valuation", "Stock Valuation", daily_valuation),
    ("sector", "Sector Analysis", daily_sector_analysis),
    ("bsc_forecast", "BSC Forecast", daily_bsc_forecast),
    ("consensus", "Consensus Comparison", daily_consensus_update),  # NEW
]
```

---

## Question 3: VCI Forecast Integration Strategy

### User's Goal

> "Mục đích khi có data VCI là để so sánh với data của BSC forecast, VCI là công ty khá consensus, tôi muốn có thêm các nguồn để track và so sánh vs số forecast của BSC"

Translation: Use VCI (consensus source) to compare against BSC forecasts, track multiple sources

### VCI Data Status

**Current:** `vci_coverage_universe.json` (83 tickers, full metadata) ✅

**Contains:**
- Target price, rating, sector
- Forward PE/PB 2025F/2026F
- ROE, NPATMI growth forecasts
- Analyst name (for consensus tracking)

### Integration Options

#### Option 1: JSON + Parquet Hybrid (RECOMMENDED)

**Approach:** Keep VCI as JSON (source format), create parquet for comparison

```python
# PROCESSORS/forecast/vci_forecast_processor.py

class VCIForecastProcessor:
    """
    Process VCI forecast metadata for consensus comparison.
    VCI data is already complete - just need to load and standardize.
    """

    def load_vci_forecasts(self) -> pd.DataFrame:
        """Load VCI JSON and convert to standard format."""
        vci_df = pd.read_json("DATA/processed/forecast/VCI/vci_coverage_universe.json")

        # Standardize column names to match BSC
        standardized = vci_df.rename(columns={
            'ticker': 'symbol',
            'targetPrice': 'target_price',
            'pe': 'pe_fwd',
            'pb': 'pb_fwd',
            'npatmiGrowth': 'npatmi_growth_yoy',
        })

        # Unnest forward years
        standardized = self._explode_forward_years(standardized)

        # Add source attribution
        standardized['source'] = 'VCI'
        standardized['analyst'] = vci_df['analyst']

        return standardized

    def _explode_forward_years(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert nested 2025F/2026F to wide format."""
        # Implementation detail...
        pass
```

**Pros:**
- Preserves source JSON (immutable reference)
- Creates comparison-ready parquet
- Simple, YAGNI-compliant

**Cons:**
- None significant

#### Option 2: Full Parquet Conversion

**Approach:** Convert VCI to parquet matching BSC schema exactly

**Pros:**
- Unified schema
- Faster loading

**Cons:**
- Loses source attribution (analyst name)
- Over-engineering for 83 tickers
- Violates YAGNI

#### Option 3: Multi-Source Consensus System

**Approach:** Build extensible system for N forecast sources

**Pros:**
- Scalable to future sources
- Clean architecture

**Cons:**
- Over-engineering (YAGNI violation)
- Only 2 sources currently
- Premature optimization

### Recommendation: Option 1 (Hybrid)

**Rationale:**
1. VCI data is ALREADY COMPLETE (just JSON standardization needed)
2. BSC processor already exists (93 tickers)
3. Simple merge operation for comparison
4. Can extend to more sources LATER (YAGNI)

**Implementation Steps:**
1. Create `PROCESSORS/forecast/vci_forecast_processor.py` (50 lines)
2. Create `PROCESSORS/pipelines/daily/daily_consensus_update.py` (80 lines)
3. Add Step 7 to master pipeline
4. Update WEBAPP forecast dashboard to show comparison

---

## Consensus Comparison Dashboard

### WEBAPP Integration

**New Tab in Forecast Dashboard:**

```python
# WEBAPP/pages/forecast/forecast_dashboard.py

tab1, tab2, tab3 = st.tabs(["BSC Forecast", "Consensus Comparison", "Divergence Alerts"])

with tab2:
    st.subheader("BSC vs VCI Consensus")

    # Load consensus data
    consensus_df = pd.read_parquet("DATA/processed/forecast/consensus/consensus_comparison.parquet")

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Coverage", f"{len(consensus_df)} tickers")
    col2.metric("Rating Agreement", f"{agreement_pct:.1f}%")
    col3.metric("Avg Target Price Diff", f"{avg_price_diff:.1f}%")

    # Comparison table
    st.dataframe(
        consensus_df[[
            'symbol', 'rating_bsc', 'rating_vci',
            'target_price_bsc', 'target_price_vci', 'target_price_divergence_pct',
            'analyst'
        ]],
        use_container_width=True
    )

with tab3:
    st.subheader("🚨 Divergence Alerts")

    divergences = pd.read_parquet("DATA/processed/forecast/consensus/consensus_divergences.parquet")

    for _, row in divergences.iterrows():
        if not row['rating_match']:
            st.error(f"{row['symbol']}: BSC={row['rating_bsc']} vs VCI={row['rating_vci']}")
        elif abs(row['target_price_divergence_pct']) > 0.15:
            st.warning(f"{row['symbol']}: Target price diff {row['target_price_divergence_pct']:.1%}")
```

---

## Data Models

### Consensus Comparison Schema

```python
# WEBAPP/core/models/data_models.py

class ConsensusComparison(BaseModel):
    """BSC vs VCI forecast comparison."""

    symbol: str
    sector: str

    # BSC data
    rating_bsc: str
    target_price_bsc: float
    pe_fwd_2025_bsc: float
    pb_fwd_2025_bsc: float

    # VCI data
    rating_vci: str
    target_price_vci: float
    pe_2025F: float
    pb_2025F: float
    analyst: str  # VCI analyst name

    # Comparison metrics
    target_price_divergence_pct: float
    rating_match: bool
    pe_fwd_2025_diff: float

    class Config:
        schema_extra = {
            "example": {
                "symbol": "ACB",
                "rating_bsc": "BUY",
                "rating_vci": "BUY",
                "target_price_bsc": 28400,
                "target_price_vci": 33300,
                "target_price_divergence_pct": 0.173,
                "rating_match": True,
                "analyst": "Nga Ho"
            }
        }
```

---

## Implementation Plan

### Phase 2: Consensus Comparison System

**Step 1: VCI Processor** (1 day)
```bash
# Create VCI forecast processor
touch PROCESSORS/forecast/vci_forecast_processor.py
# Load JSON, standardize columns, add source attribution
```

**Step 2: Consensus Update Script** (1 day)
```bash
# Create daily consensus comparison
touch PROCESSORS/pipelines/daily/daily_consensus_update.py
# Merge BSC + VCI, calculate divergences
```

**Step 3: Pipeline Integration** (0.5 day)
```bash
# Add Step 7 to master pipeline
# Update DAILY_PIPELINE_SUMMARY.md
```

**Step 4: WEBAPP Dashboard** (2 days)
```bash
# Add Consensus Comparison tab
# Add Divergence Alerts tab
# Update data models
```

**Total: 4.5 days**

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| VCI JSON format changes | Low | Medium | Version the JSON schema |
| Ticker mismatch | Medium | Low | Use fuzzy matching |
| Missing VCI updates | Medium | High | Add stale data alert |
| BSC/VCI coverage gap | Low | Low | Show coverage stats |

---

## Success Criteria

1. **Pipeline**: Daily update runs without errors
2. **Data**: Consensus parquet generated with >50 overlapping tickers
3. **Dashboard**: Comparison tab shows divergences correctly
4. **Alerts**: Divergences flagged (rating mismatch OR >15% price diff)
5. **Performance**: Consensus update <30 seconds

---

## Future Extensions (YAGNI - Do Later)

1. **Additional Sources**: SSI, VCSC, VNDirect forecasts
2. **Consensus Scoring**: Weighted average across N sources
3. **Historical Tracking**: Track forecast accuracy over time
4. **Analyst Ranking**: Rank analysts by historical accuracy
5. **Auto-Alerts**: Email/Slack on significant divergences

---

## Unresolved Questions

1. **VCI Update Frequency**: How often does VCI update their forecasts?
2. **VCI API Access**: Is there an API or manual Excel download?
3. **Analyst Tracking**: Do we want to track individual analyst accuracy?
4. **Historical VCI**: Do we have historical VCI forecasts for backtesting?

---

## Decision Summary

### Approved Changes

1. **Phase 1 → Path Migration** (rename old Phase 0.5)
2. **Old Phase 1 → SKIP** (already implemented in `PROCESSORS/sector/`)
3. **Add Step 7 to Pipeline**: Consensus Comparison (BSC vs VCI)
4. **VCI Integration**: Hybrid approach (JSON source + parquet comparison)
5. **WEBAPP**: Add Consensus Comparison & Divergence Alerts tabs

### Next Steps

1. Update `CLAUDE.md` phase definitions
2. Create `PROCESSORS/forecast/vci_forecast_processor.py`
3. Create `PROCESSORS/pipelines/daily/daily_consensus_update.py`
4. Add Step 7 to `run_all_daily_updates.py`
5. Update forecast dashboard with consensus tabs

---

**Report End**
