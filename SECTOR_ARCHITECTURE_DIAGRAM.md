# 🏗️ SECTOR PROCESSING ARCHITECTURE - VISUAL GUIDE
**Kiến trúc hệ thống xử lý ngành - Hướng dẫn trực quan**

Date: 2025-12-15

---

## 📊 CURRENT STATE (3 Systems - Overlapping)

```
┌────────────────────────────────────────────────────────────────────┐
│                    CURRENT FRAGMENTED ARCHITECTURE                  │
└────────────────────────────────────────────────────────────────────┘

📁 SYSTEM 1: PROCESSORS/sector/                    [STATUS: ✅ COMPLETE]
   │
   ├─ sector_processor.py (Main Orchestrator)
   ├─ calculators/
   │  ├─ fa_aggregator.py          → sector_fundamental_metrics.parquet
   │  └─ ta_aggregator.py          → sector_valuation_metrics.parquet
   ├─ scoring/
   │  ├─ fa_scorer.py
   │  ├─ ta_scorer.py
   │  └─ signal_generator.py      → sector_combined_scores.parquet
   └─ daily_sector_valuation_update.py

   OUTPUT: 3 files in DATA/processed/sector/
   PURPOSE: Complete FA+TA analysis with signals


📁 SYSTEM 2: PROCESSORS/valuation/calculators/    [STATUS: ⚠️ REDUNDANT]
   │
   └─ sector_valuation_calculator.py
      │
      ├─ Inherits from VNIndexValuationCalculator
      ├─ Loops through all sectors
      └─ Calls parent.calculate_scope_valuation()

   OUTPUT: sector_valuation.parquet in DATA/processed/valuation/sector_pe/
   PURPOSE: Sector PE/PB historical tracking
   PROBLEM: Just a wrapper around parent class! ❌


📁 SYSTEM 3: PROCESSORS/valuation/calculators/    [STATUS: ✅ POWERFUL BASE]
   │
   └─ vnindex_valuation_calculator.py
      │
      ├─ calculate_scope_valuation(scope, symbols)  ← Generic calculator
      └─ process_all_scopes()                        ← Batch processor

   OUTPUT: vnindex_valuation_refined.parquet in DATA/processed/valuation/vnindex/
   PURPOSE: Market-wide PE/PB + Forward PE (BSC forecast)
   POWER: Can calculate ANY scope (market, sector, custom index)


🔴 PROBLEMS:
   1. System 2 is redundant wrapper of System 3
   2. Sector PE/PB data split across 2 locations
   3. Different schemas for same metrics
   4. Two separate daily update scripts
```

---

## 🎯 PROPOSED UNIFIED ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                   UNIFIED CLEAN ARCHITECTURE                        │
└────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 USE CASE 1: SECTOR ANALYSIS (FA + TA + SIGNALS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 PROCESSORS/sector/
   │
   ├─ sector_processor.py ───────────────────┐
   │                                          │
   │  ┌───────────────────────────────────┐  │
   │  │  Step 1: FA Aggregation           │  │
   │  │  fa_aggregator.py                 │  │
   │  │  ↓                                 │  │
   │  │  Load: company_full.parquet       │  │
   │  │        bank_full.parquet           │  │
   │  │        security_full.parquet       │  │
   │  │  ↓                                 │  │
   │  │  Pivot: METRIC_CODE → Business    │  │
   │  │  ↓                                 │  │
   │  │  Aggregate: By sector + date      │  │
   │  │  ↓                                 │  │
   │  │  Calculate: Ratios + Growth       │  │
   │  └───────────────────────────────────┘  │
   │               ↓                          │
   │  📊 sector_fundamental_metrics.parquet   │
   │     [sector_code, report_date,          │
   │      total_revenue, net_profit,         │
   │      roe, roa, debt_to_equity,          │
   │      revenue_growth_yoy, ...]           │
   │                                          │
   │  ┌───────────────────────────────────┐  │
   │  │  Step 2: TA Aggregation           │  │
   │  │  ta_aggregator.py                 │  │
   │  │  ↓                                 │  │
   │  │  Load: OHLCV + PE/PB data         │  │
   │  │  ↓                                 │  │
   │  │  Aggregate: By sector + date      │  │
   │  │  ↓                                 │  │
   │  │  Calculate: Valuation + Technical │  │
   │  └───────────────────────────────────┘  │
   │               ↓                          │
   │  📊 sector_valuation_metrics.parquet    │
   │     [sector_code, date,                 │
   │      sector_pe, sector_pb, sector_ps,   │
   │      ma_20, rsi_14, ...]                │
   │                                          │
   │  ┌───────────────────────────────────┐  │
   │  │  Step 3: Scoring + Signals        │  │
   │  │  fa_scorer.py + ta_scorer.py      │  │
   │  │  signal_generator.py              │  │
   │  │  ↓                                 │  │
   │  │  FA Score: ROE, margins, growth   │  │
   │  │  TA Score: PE, PB, technical      │  │
   │  │  ↓                                 │  │
   │  │  Signal: BUY/SELL/HOLD            │  │
   │  └───────────────────────────────────┘  │
   │               ↓                          │
   │  📊 sector_combined_scores.parquet      │
   │     [sector_code, date,                 │
   │      fa_score, ta_score,                │
   │      combined_score, signal]            │
   └──────────────────────────────────────────┘

   🎯 DASHBOARD: Sector Analysis Dashboard
      - Compare sectors by FA/TA scores
      - Investment recommendations
      - Sector rotation strategies


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 USE CASE 2: MARKET & SECTOR VALUATION (PE/PB HISTORICAL + FORWARD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 PROCESSORS/valuation/calculators/
   │
   └─ vnindex_valuation_calculator.py ──────────────┐
      │                                              │
      │  ┌──────────────────────────────────────┐   │
      │  │  Universal Scope Calculator          │   │
      │  │  calculate_scope_valuation()         │   │
      │  │  ↓                                    │   │
      │  │  Load: OHLCV + Fundamentals          │   │
      │  │  ↓                                    │   │
      │  │  Filter: By symbols (whitelist/      │   │
      │  │          blacklist)                   │   │
      │  │  ↓                                    │   │
      │  │  Merge: Market cap + Earnings +      │   │
      │  │         Equity                        │   │
      │  │  ↓                                    │   │
      │  │  Aggregate: Sum(MC) / Sum(Earnings)  │   │
      │  │             Sum(MC) / Sum(Equity)    │   │
      │  │  ↓                                    │   │
      │  │  Forward PE: Using BSC forecast      │   │
      │  └──────────────────────────────────────┘   │
      │                                              │
      │  ┌──────────────────────────────────────┐   │
      │  │  Batch Processor                     │   │
      │  │  process_all_scopes()                │   │
      │  │  ↓                                    │   │
      │  │  Loop through:                       │   │
      │  │    1. VNINDEX                        │   │
      │  │    2. VNINDEX_EXCLUDE (no VIC/VHM)   │   │
      │  │    3. BSC_INDEX (BSC coverage)       │   │
      │  │    4. SECTOR:Banking                 │   │
      │  │    5. SECTOR:RealEstate              │   │
      │  │    ... (all 19 sectors)              │   │
      │  │  ↓                                    │   │
      │  │  Combine all results                 │   │
      │  └──────────────────────────────────────┘   │
      │               ↓                              │
      │  📊 unified_pe_pb_valuation.parquet         │
      │     [date, scope, scope_type,               │
      │      pe_ttm, pb, pe_fwd_2025, pe_fwd_2026,  │
      │      total_mc, total_earnings, total_equity]│
      │                                              │
      │     Examples:                                │
      │     VNINDEX            | MARKET | 15.2 | 2.1│
      │     VNINDEX_EXCLUDE    | MARKET | 17.3 | 2.3│
      │     SECTOR:Banking     | SECTOR | 8.2  | 1.3│
      │     SECTOR:RealEstate  | SECTOR | 22.1 | 2.8│
      └──────────────────────────────────────────────┘

   🎯 DASHBOARDS:
      - VN-Index PE/PB historical trends
      - Sector PE/PB comparison
      - Forward PE vs Trailing PE analysis
      - Valuation percentile tracking


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DAILY UPDATE WORKFLOWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────┐
│  UPDATE 1: Sector FA+TA Analysis (Weekly/Quarterly)     │
└──────────────────────────────────────────────────────────┘

$ python3 PROCESSORS/sector/run_sector_analysis.py

┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ FA Aggregator  │────▶│  TA Aggregator │────▶│ Score+Signals  │
└────────────────┘     └────────────────┘     └────────────────┘
        ↓                      ↓                       ↓
  sector_fundamental   sector_valuation    sector_combined
     _metrics.pq         _metrics.pq          _scores.pq

  FREQUENCY: When new quarterly reports available


┌──────────────────────────────────────────────────────────┐
│  UPDATE 2: Market & Sector Valuation (Daily)            │
└──────────────────────────────────────────────────────────┘

$ python3 PROCESSORS/valuation/daily_market_sector_valuation_update.py

┌──────────────────────────────────────────┐
│  VNIndexValuationCalculator              │
│                                          │
│  process_all_scopes(                     │
│    include_sectors=True,                 │
│    target_date='2024-12-15'              │
│  )                                       │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│  Calculate:                              │
│    - VNINDEX                             │
│    - VNINDEX_EXCLUDE                     │
│    - BSC_INDEX                           │
│    - All 19 sectors                      │
└──────────────────────────────────────────┘
                  ↓
      unified_pe_pb_valuation.parquet
        (append mode - daily update)

  FREQUENCY: Every trading day
```

---

## 🔄 DATA FLOW COMPARISON

### **BEFORE (Current - Fragmented):**

```
DATA/processed/
├── sector/
│   ├── sector_fundamental_metrics.parquet     ← From PROCESSORS/sector/
│   ├── sector_valuation_metrics.parquet       ← From PROCESSORS/sector/
│   └── sector_combined_scores.parquet         ← From PROCESSORS/sector/
│
└── valuation/
    ├── vnindex/
    │   └── vnindex_valuation_refined.parquet  ← From vnindex_calculator
    │       [VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX only]
    │
    └── sector_pe/
        └── sector_valuation.parquet           ← From sector_calculator
            [Sector PE/PB - DUPLICATE DATA!]

❌ PROBLEMS:
   - Sector PE/PB split across 2 locations
   - Different schemas for same metrics
   - sector_valuation_calculator is just wrapper
```

### **AFTER (Proposed - Unified):**

```
DATA/processed/
├── sector/
│   ├── sector_fundamental_metrics.parquet     ← FA metrics (quarterly)
│   ├── sector_valuation_metrics.parquet       ← TA metrics (daily)
│   └── sector_combined_scores.parquet         ← Scores + signals (daily)
│
└── valuation/
    └── market_sector_valuation/
        └── unified_pe_pb_valuation.parquet    ← VNINDEX + Sectors (daily)
            [date, scope, scope_type, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]

            scope examples:
            - VNINDEX
            - VNINDEX_EXCLUDE
            - BSC_INDEX
            - SECTOR:Banking
            - SECTOR:RealEstate
            - ... (all 19 sectors)

✅ BENEFITS:
   - Single source of truth for PE/PB
   - Unified schema
   - Easy to query: df[df['scope_type'] == 'SECTOR']
   - Easy to compare: VNINDEX vs specific sector
```

---

## 🎯 USE CASE MATRIX

| Use Case | Data Source | Frequency | Purpose |
|----------|-------------|-----------|---------|
| **Sector FA Analysis** | `sector_fundamental_metrics.parquet` | Quarterly | Compare sectors by fundamentals (ROE, margins, growth) |
| **Sector TA Analysis** | `sector_valuation_metrics.parquet` | Daily | Compare sectors by valuation + technical |
| **Sector Recommendations** | `sector_combined_scores.parquet` | Daily | Investment signals (BUY/SELL/HOLD) |
| **Market PE/PB Trend** | `unified_pe_pb_valuation.parquet` (scope='VNINDEX') | Daily | Track market valuation over time |
| **Sector PE/PB Trend** | `unified_pe_pb_valuation.parquet` (scope='SECTOR:*') | Daily | Track sector valuation over time |
| **Forward PE Analysis** | `unified_pe_pb_valuation.parquet` (pe_fwd_2025) | Daily | Compare trailing PE vs forward PE |
| **Sector Rotation** | Combined: scores + PE/PB | Daily | Identify overvalued/undervalued sectors |

---

## 🔧 IMPLEMENTATION TASKS

### **Task 1: Enhance vnindex_valuation_calculator.py**
```python
# Add sector support
def __init__(self):
    self.sector_reg = SectorRegistry()

# Add batch processor
def process_all_scopes(self, include_sectors=True):
    results = []

    # Market scopes
    results.append(self.calculate_scope_valuation('VNINDEX'))
    results.append(self.calculate_scope_valuation('VNINDEX_EXCLUDE',
                                                   excluded_symbols=['VIC','VHM']))

    # Sector scopes
    if include_sectors:
        for sector in self.sector_reg.get_all_sectors():
            symbols = self.sector_reg.get_tickers_by_sector(sector)
            results.append(self.calculate_scope_valuation(
                f'SECTOR:{sector}',
                subset_symbols=symbols
            ))

    return pd.concat(results)
```

### **Task 2: Delete sector_valuation_calculator.py**
```bash
git rm PROCESSORS/valuation/calculators/sector_valuation_calculator.py
```

### **Task 3: Create daily_market_sector_valuation_update.py**
```python
class DailyValuationUpdater:
    def update_daily(self, target_date=None):
        # Calculate all scopes
        new_data = self.calc.process_all_scopes(
            include_sectors=True,
            target_date=target_date
        )

        # Append to unified file
        self._append_to_file(new_data)
```

---

## 📊 QUERY EXAMPLES

### **After Implementation:**

```python
# Load unified data
df = pd.read_parquet("DATA/processed/valuation/market_sector_valuation/unified_pe_pb_valuation.parquet")

# Query 1: Get VNINDEX PE history
vnindex_pe = df[df['scope'] == 'VNINDEX'][['date', 'pe_ttm', 'pb']]

# Query 2: Get all sector PE on specific date
latest_date = df['date'].max()
sector_pe = df[
    (df['scope_type'] == 'SECTOR') &
    (df['date'] == latest_date)
][['scope', 'pe_ttm', 'pb', 'pe_fwd_2025']]

# Query 3: Compare Banking PE vs VNINDEX PE
banking_vs_market = df[df['scope'].isin(['VNINDEX', 'SECTOR:Banking'])]

# Query 4: Find cheapest sectors (lowest PE)
latest_sectors = df[(df['scope_type'] == 'SECTOR') & (df['date'] == latest_date)]
cheapest = latest_sectors.nsmallest(5, 'pe_ttm')[['scope', 'pe_ttm', 'pb']]

# Query 5: Compare trailing PE vs forward PE (discount/premium)
df['pe_gap'] = df['pe_ttm'] - df['pe_fwd_2025']
df['pe_gap_pct'] = (df['pe_gap'] / df['pe_fwd_2025']) * 100
```

---

## ✅ SUCCESS METRICS

After implementation, you should be able to:

1. ✅ Run ONE daily script to update market + all sectors
2. ✅ Query sector PE/PB from ONE unified file
3. ✅ Compare VNINDEX vs any sector easily
4. ✅ Track forward PE (2025/2026) for all scopes
5. ✅ No duplicate code (sector_calculator deleted)
6. ✅ No duplicate data (one PE/PB file only)
7. ✅ Clear separation: Sector analysis (FA+TA+signals) vs Valuation tracking (PE/PB history)

---

**END OF VISUALIZATION** 🎨
