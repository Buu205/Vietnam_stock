# 📊 SECTOR PROCESSING CONSOLIDATION PLAN
**Kế hoạch hợp nhất và tổ chức lại hệ thống xử lý ngành**

Date: 2025-12-15
Author: Claude Code
Version: 1.0.0

---

## 🔍 CURRENT STATE ANALYSIS

### **Hiện tại có 3 hệ thống xử lý sector đang chồng chéo:**

#### 1️⃣ **PROCESSORS/sector/** (Complete FA+TA Pipeline) ✅ KEEP
```
PROCESSORS/sector/
├── sector_processor.py           # Main orchestrator
├── calculators/
│   ├── fa_aggregator.py         # FA metrics by sector
│   ├── ta_aggregator.py         # TA/Valuation metrics by sector
│   ├── base_aggregator.py       # Base class
│   └── metric_mappings.py       # Metric code → Business metrics
├── scoring/
│   ├── fa_scorer.py             # FA scoring (ROE, margins, growth)
│   ├── ta_scorer.py             # TA scoring (PE, PB, technical)
│   └── signal_generator.py      # BUY/SELL/HOLD signals
└── daily_sector_valuation_update.py  # Daily update script

OUTPUT:
✅ DATA/processed/sector/sector_fundamental_metrics.parquet
✅ DATA/processed/sector/sector_valuation_metrics.parquet
✅ DATA/processed/sector/sector_combined_scores.parquet

PURPOSE: Unified sector analysis dashboard (FA+TA combined)
```

#### 2️⃣ **PROCESSORS/valuation/calculators/sector_valuation_calculator.py** ⚠️ MERGE
```python
# Inherits from VNIndexValuationCalculator
# Calculates sector PE/PB (market-cap weighted)
# Output: DATA/processed/valuation/sector_pe/sector_valuation.parquet

class SectorValuationCalculator(VNIndexValuationCalculator):
    def process_all_sectors() -> pd.DataFrame:
        # Calculate PE/PB for all sectors
        # Returns: [date, scope, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]
```

#### 3️⃣ **PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py** ✅ KEEP
```python
# Base calculator for market-wide valuation
# Supports multiple scopes: VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX, Sectors
# Forward PE using BSC forecast data

class VNIndexValuationCalculator:
    def calculate_scope_valuation(scope_name, subset_symbols, excluded_symbols):
        # Generic scope calculator (market, sector, custom index)
        # Returns: [date, scope, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]
```

---

## 🎯 CONSOLIDATION STRATEGY

### **KEEP 2 SYSTEMS, MERGE 1:**

```
┌─────────────────────────────────────────────────────────────────┐
│                 SECTOR ANALYSIS ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│ SYSTEM 1: SECTOR FUNDAMENTAL + TECHNICAL ANALYSIS                     │
│ Location: PROCESSORS/sector/                                          │
│ Purpose: Complete sector analysis with FA+TA scores & signals         │
└───────────────────────────────────────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │ FA Aggregator (fa_aggregator.py)    │
    │ - Load *_full.parquet               │
    │ - Pivot metric_code → business      │
    │ - Aggregate by sector               │
    │ - Calculate ratios & growth         │
    └─────────────────────────────────────┘
        ↓
    sector_fundamental_metrics.parquet
    [sector_code, report_date, total_revenue, net_profit,
     roe, roa, debt_to_equity, revenue_growth_yoy, ...]

        ↓
    ┌─────────────────────────────────────┐
    │ TA Aggregator (ta_aggregator.py)    │
    │ - Load OHLCV + valuation data       │
    │ - Aggregate by sector               │
    │ - Calculate PE, PB, PS, EV/EBITDA   │
    │ - Technical indicators              │
    └─────────────────────────────────────┘
        ↓
    sector_valuation_metrics.parquet
    [sector_code, date, sector_pe, sector_pb, sector_ps,
     sector_ev_ebitda, sector_market_cap, ma_20, rsi_14, ...]

        ↓
    ┌─────────────────────────────────────┐
    │ Scorers + Signal Generator          │
    │ - FA Scorer: Score fundamentals     │
    │ - TA Scorer: Score valuation/tech   │
    │ - Signal: BUY/SELL/HOLD             │
    └─────────────────────────────────────┘
        ↓
    sector_combined_scores.parquet
    [sector_code, date, fa_score, ta_score,
     combined_score, signal, recommendation]


┌───────────────────────────────────────────────────────────────────────┐
│ SYSTEM 2: MARKET & SECTOR PE/PB VALUATION (VNINDEX Calculator)       │
│ Location: PROCESSORS/valuation/calculators/                          │
│ Purpose: Historical PE/PB tracking + Forward PE (BSC forecast)        │
└───────────────────────────────────────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────────────────┐
    │ VNIndexValuationCalculator                      │
    │ - Calculate_scope_valuation()                   │
    │   → Generic scope calculator                    │
    │   → Supports: VNINDEX, Sectors, Custom indices  │
    │ - Forward PE using BSC forecast                 │
    └─────────────────────────────────────────────────┘
        ↓
    DATA/processed/valuation/vnindex/
    ├── vnindex_valuation_refined.parquet
    │   [date, scope, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]
    │
    └── (MERGE HERE) sector PE/PB data
        Should be part of vnindex_valuation_refined.parquet
        with scope='SECTOR:Banking', scope='SECTOR:RealEstate', etc.
```

---

## 📋 DETAILED CONSOLIDATION PLAN

### **PHASE 1: KEEP PROCESSORS/sector/ AS PRIMARY SECTOR ANALYSIS** ✅

**NO CHANGES NEEDED** - This system is complete and well-designed:

```python
# PROCESSORS/sector/sector_processor.py
class SectorProcessor:
    def run_full_pipeline():
        # 1. FA Aggregation → sector_fundamental_metrics.parquet
        # 2. TA Aggregation → sector_valuation_metrics.parquet
        # 3. FA Scoring → FA scores
        # 4. TA Scoring → TA scores
        # 5. Signal Generation → sector_combined_scores.parquet
```

**KEY FEATURES:**
- ✅ Complete FA+TA integration
- ✅ Scoring & signal generation
- ✅ Uses registries (MetricRegistry, SectorRegistry)
- ✅ Configurable weights (ConfigManager)
- ✅ Daily update script ready

**OUTPUT FILES:**
```
DATA/processed/sector/
├── sector_fundamental_metrics.parquet      # FA metrics (quarterly)
├── sector_valuation_metrics.parquet        # TA/valuation metrics (daily)
└── sector_combined_scores.parquet          # Scores + signals (daily)
```

---

### **PHASE 2: MERGE sector_valuation_calculator.py INTO vnindex_valuation_calculator.py** 🔄

#### **Current Duplication:**

```python
# ❌ DUPLICATE: sector_valuation_calculator.py
class SectorValuationCalculator(VNIndexValuationCalculator):
    def process_all_sectors():
        sectors = self.get_sectors()
        for sector in sectors:
            symbols = self.get_symbols_for_sector(sector)
            df = self.calculate_scope_valuation(
                scope_name=sector,
                subset_symbols=symbols
            )
        return df
```

**PROBLEM:** This just loops through sectors and calls parent class method!

#### **Solution: Delete sector_valuation_calculator.py and use VNIndexValuationCalculator directly**

```python
# ✅ UNIFIED: vnindex_valuation_calculator.py
class VNIndexValuationCalculator:
    """
    Universal scope calculator for market/sector PE/PB valuation.
    Supports:
    - VNINDEX (all tickers)
    - VNINDEX_EXCLUDE (exclude VIC, VHM, etc.)
    - BSC_INDEX (BSC forecast tickers)
    - SECTOR:Banking, SECTOR:RealEstate, etc.
    """

    def calculate_scope_valuation(
        scope_name: str,
        subset_symbols: list = None,
        excluded_symbols: list = None,
        bsc_forecast_df: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Calculate PE/PB for any scope (market or sector).

        Returns:
            [date, scope, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026,
             total_mc, total_earnings, total_equity]
        """

    def process_all_scopes(
        include_sectors: bool = True,
        exclude_list: list = None
    ) -> pd.DataFrame:
        """
        Process VNINDEX + sectors in one run.

        Args:
            include_sectors: If True, calculate all sectors
            exclude_list: Symbols to exclude from VNINDEX_EXCLUDE

        Returns:
            Combined DataFrame with all scopes:
            - VNINDEX
            - VNINDEX_EXCLUDE
            - BSC_INDEX
            - SECTOR:Banking
            - SECTOR:RealEstate
            - ... (all 19 sectors)
        """
        results = []

        # 1. VNINDEX
        results.append(self.calculate_scope_valuation('VNINDEX'))

        # 2. VNINDEX_EXCLUDE
        results.append(self.calculate_scope_valuation(
            'VNINDEX_EXCLUDE',
            excluded_symbols=exclude_list
        ))

        # 3. BSC_INDEX
        if bsc_symbols:
            results.append(self.calculate_scope_valuation(
                'BSC_INDEX',
                subset_symbols=bsc_symbols,
                bsc_forecast_df=forecast_df
            ))

        # 4. ALL SECTORS
        if include_sectors:
            for sector in self.sector_registry.get_all_sectors():
                symbols = self.sector_registry.get_tickers_by_sector(sector)
                results.append(self.calculate_scope_valuation(
                    f'SECTOR:{sector}',
                    subset_symbols=symbols
                ))

        return pd.concat(results)
```

---

### **PHASE 3: UPDATE OUTPUT PATHS & DATA CONSOLIDATION** 📁

#### **Current Output Separation:**

```
❌ FRAGMENTED:
DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet
    [date, scope='VNINDEX', pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]

DATA/processed/valuation/sector_pe/sector_valuation.parquet
    [date, scope='Banking', pe_ttm, pb, ...]

DATA/processed/sector/sector_valuation_metrics.parquet
    [date, sector_code='Banking', sector_pe, sector_pb, ...]
```

#### **Unified Output Structure:**

```
✅ UNIFIED:
DATA/processed/valuation/market_sector_valuation/
└── unified_pe_pb_valuation.parquet
    [date, scope, scope_type, pe_ttm, pb, ps, ev_ebitda,
     pe_fwd_2025, pe_fwd_2026, total_mc, total_earnings, total_equity]

    Where scope_type:
    - 'MARKET' (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
    - 'SECTOR' (Banking, RealEstate, Technology, ...)

Examples:
    date       | scope              | scope_type | pe_ttm | pb   | pe_fwd_2025
    -----------|--------------------|-----------:|-------:|-----:|------------
    2024-12-15 | VNINDEX            | MARKET     | 15.2   | 2.1  | 13.8
    2024-12-15 | VNINDEX_EXCLUDE    | MARKET     | 17.3   | 2.3  | 15.1
    2024-12-15 | BSC_INDEX          | MARKET     | 14.5   | 2.0  | 12.9
    2024-12-15 | SECTOR:Banking     | SECTOR     | 8.2    | 1.3  | 7.5
    2024-12-15 | SECTOR:RealEstate  | SECTOR     | 22.1   | 2.8  | 18.7
```

---

### **PHASE 4: CREATE DAILY UPDATE PIPELINE** 🔄

#### **Unified Daily Update Script:**

```python
# PROCESSORS/valuation/daily_market_sector_valuation_update.py

class DailyValuationUpdater:
    """
    Daily update for market & sector PE/PB valuation.

    Updates:
    1. VNINDEX PE/PB (all tickers)
    2. VNINDEX_EXCLUDE PE/PB (exclude conglomerates)
    3. BSC_INDEX PE/PB (BSC coverage universe)
    4. All 19 sectors PE/PB
    5. Forward PE using BSC forecast
    """

    def __init__(self):
        self.calc = VNIndexValuationCalculator()
        self.output_path = Path("DATA/processed/valuation/market_sector_valuation")

    def update_daily(self, target_date: str = None):
        """Run daily update for latest trading date."""

        # Get latest trading date
        if target_date is None:
            target_date = self._get_latest_trading_date()

        logger.info(f"Updating valuation for {target_date}")

        # Calculate all scopes
        new_data = self.calc.process_all_scopes(
            include_sectors=True,
            exclude_list=['VIC', 'VHM', 'VRE', 'MSN'],
            start_date=target_date,
            end_date=target_date
        )

        # Append to existing file
        self._append_to_file(new_data)

        # Print summary
        self._print_summary(new_data)

    def backfill_history(self, start_date: str, end_date: str):
        """Backfill historical data."""
        logger.info(f"Backfilling {start_date} to {end_date}")

        all_data = self.calc.process_all_scopes(
            include_sectors=True,
            start_date=start_date,
            end_date=end_date
        )

        # Replace file (full history rebuild)
        self._save_full_history(all_data)
```

---

## 🏗️ IMPLEMENTATION STEPS

### **Step 1: Enhance VNIndexValuationCalculator** (2 hours)

**File:** `PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py`

**Changes:**
1. Add `sector_registry` integration:
   ```python
   from config.registries import SectorRegistry

   def __init__(self):
       self.sector_reg = SectorRegistry()
   ```

2. Add `process_all_scopes()` method (combines market + sectors)

3. Add scope type classification:
   ```python
   def get_scope_type(self, scope_name: str) -> str:
       if scope_name in ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']:
           return 'MARKET'
       elif scope_name.startswith('SECTOR:'):
           return 'SECTOR'
       else:
           return 'CUSTOM'
   ```

4. Update output schema:
   ```python
   result_df['scope_type'] = result_df['scope'].apply(self.get_scope_type)
   ```

---

### **Step 2: Delete sector_valuation_calculator.py** (10 minutes)

**File:** `PROCESSORS/valuation/calculators/sector_valuation_calculator.py`

**Action:**
```bash
git rm PROCESSORS/valuation/calculators/sector_valuation_calculator.py
git commit -m "refactor: Merge sector_valuation_calculator into vnindex_valuation_calculator"
```

**Reason:** Redundant - all functionality is in parent class

---

### **Step 3: Create Unified Daily Update Script** (1 hour)

**File:** `PROCESSORS/valuation/daily_market_sector_valuation_update.py`

**Features:**
- Update VNINDEX + all sectors in one run
- Append to unified output file
- Compare with previous day
- Print summary of changes

**Run:**
```bash
# Daily update (latest trading date)
python3 PROCESSORS/valuation/daily_market_sector_valuation_update.py

# Specific date
python3 PROCESSORS/valuation/daily_market_sector_valuation_update.py --date 2024-12-15

# Backfill history
python3 PROCESSORS/valuation/daily_market_sector_valuation_update.py --backfill --start 2020-01-01
```

---

### **Step 4: Update Documentation** (30 minutes)

**Update files:**
1. `CLAUDE.md` - Document new unified structure
2. `README.md` - Update daily update commands
3. `PROCESSORS/valuation/README.md` - Explain valuation calculators

---

### **Step 5: Migrate Existing Data** (Optional - 1 hour)

**Goal:** Combine historical data into unified format

```python
# scripts/migrate_valuation_data.py

def migrate_vnindex_to_unified():
    # Load old vnindex data
    vnindex_df = pd.read_parquet("DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet")

    # Load old sector PE data
    sector_df = pd.read_parquet("DATA/processed/valuation/sector_pe/sector_valuation.parquet")

    # Standardize schema
    vnindex_df['scope_type'] = 'MARKET'
    sector_df['scope_type'] = 'SECTOR'
    sector_df['scope'] = 'SECTOR:' + sector_df['scope']

    # Combine
    unified = pd.concat([vnindex_df, sector_df])

    # Save
    unified.to_parquet("DATA/processed/valuation/market_sector_valuation/unified_pe_pb_valuation.parquet")
```

---

## 📊 FINAL ARCHITECTURE SUMMARY

### **Two Independent Systems:**

#### **System 1: Sector Analysis (PROCESSORS/sector/)**
```
Purpose: Complete sector fundamental + technical analysis
Output:
  - sector_fundamental_metrics.parquet (quarterly FA metrics)
  - sector_valuation_metrics.parquet (daily TA/valuation metrics)
  - sector_combined_scores.parquet (scores + BUY/SELL/HOLD signals)

Use Cases:
  - Sector comparison dashboard
  - FA vs TA analysis
  - Investment recommendations
  - Sector rotation strategies
```

#### **System 2: Market & Sector Valuation (PROCESSORS/valuation/)**
```
Purpose: Historical PE/PB tracking + Forward PE forecast
Output:
  - unified_pe_pb_valuation.parquet
    (VNINDEX + all sectors in one file, with forward PE)

Use Cases:
  - Market PE/PB historical trends
  - Sector PE/PB historical trends
  - Forward PE analysis (BSC forecast)
  - Valuation percentile tracking
  - Compare VNINDEX vs VNINDEX_EXCLUDE
```

### **Data Relationship:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─→ DATA/raw/ohlcv/OHLCV_mktcap.parquet (market cap, price)
    ├─→ DATA/processed/fundamental/*_full.parquet (financials)
    └─→ DATA/processed/forecast/Database Forecast BSC.xlsx (forward)

    ↓
┌─────────────────────────────────────────────────────────────────┐
│              SYSTEM 1: SECTOR ANALYSIS                           │
│              (PROCESSORS/sector/)                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─→ FA Aggregator → sector_fundamental_metrics.parquet
    │   [sector_code, report_date, revenue, profit, roe, roa, growth_yoy]
    │
    ├─→ TA Aggregator → sector_valuation_metrics.parquet
    │   [sector_code, date, sector_pe, sector_pb, ma_20, rsi_14]
    │
    └─→ Signal Generator → sector_combined_scores.parquet
        [sector_code, date, fa_score, ta_score, signal, recommendation]

    ↓
┌─────────────────────────────────────────────────────────────────┐
│         SYSTEM 2: MARKET & SECTOR PE/PB VALUATION               │
│         (PROCESSORS/valuation/)                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    └─→ VNIndexValuationCalculator → unified_pe_pb_valuation.parquet
        [date, scope, scope_type, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026]

        scopes: VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX,
                SECTOR:Banking, SECTOR:RealEstate, ...
```

---

## ✅ BENEFITS OF THIS CONSOLIDATION

### **1. Clear Separation of Concerns**
- ✅ Sector Analysis = Complete FA+TA with scoring & signals
- ✅ Valuation Tracking = Historical PE/PB + Forward PE forecast

### **2. No Duplication**
- ❌ Removed: sector_valuation_calculator.py (redundant child class)
- ✅ Unified: All PE/PB calculation in VNIndexValuationCalculator

### **3. Better Data Organization**
- ✅ Market + Sector valuation in ONE unified file
- ✅ Easy to query: `df[df['scope_type'] == 'SECTOR']`
- ✅ Easy to compare: VNINDEX vs specific sector

### **4. Efficient Updates**
- ✅ One daily script updates VNINDEX + all sectors
- ✅ Append mode for incremental updates
- ✅ Support for backfill

### **5. Flexible Analysis**
- ✅ Compare sector PE vs VNINDEX PE
- ✅ Track sector valuation percentiles
- ✅ Analyze forward PE vs trailing PE gap
- ✅ Identify overvalued/undervalued sectors

---

## 🚀 NEXT STEPS

### **Immediate Actions:**
1. ✅ Review this plan with user
2. ⏳ Implement Step 1: Enhance VNIndexValuationCalculator
3. ⏳ Implement Step 2: Delete sector_valuation_calculator.py
4. ⏳ Implement Step 3: Create daily update script
5. ⏳ Update CLAUDE.md with new architecture

### **Future Enhancements:**
- [ ] Add PS (Price-to-Sales) ratio to valuation metrics
- [ ] Add EV/EBITDA to valuation metrics
- [ ] Track valuation percentiles (5Y, 10Y)
- [ ] Implement alert system (sector over/undervalued)
- [ ] Create sector rotation backtest framework

---

## 📞 QUESTIONS FOR USER

1. **Keep or delete** `PROCESSORS/sector/daily_sector_valuation_update.py`?
   - Current: Updates only TA metrics (sector_valuation_metrics.parquet)
   - Proposal: Keep it as-is for sector analysis dashboard

2. **Migrate historical data** from old files to unified format?
   - Option A: Migrate (1 hour work, clean start)
   - Option B: Keep both (old + new format coexist)

3. **Output file name** for unified valuation:
   - Option A: `unified_pe_pb_valuation.parquet` (clear)
   - Option B: `market_sector_valuation.parquet` (concise)
   - Option C: Keep user preference

4. **Add PS and EV/EBITDA** to unified valuation now or later?
   - Now: More complete but more work
   - Later: Incremental addition

---

## 📚 REFERENCES

### **Key Files:**
- [sector_processor.py](PROCESSORS/sector/sector_processor.py:1-453)
- [fa_aggregator.py](PROCESSORS/sector/calculators/fa_aggregator.py:1-1126)
- [sector_valuation_calculator.py](PROCESSORS/valuation/calculators/sector_valuation_calculator.py:1-99)
- [vnindex_valuation_calculator.py](PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py:1-437)

### **Documentation:**
- [CLAUDE.md](CLAUDE.md) - Project instructions
- [README.md](README.md) - User-facing documentation

---

**END OF PLAN** 📋
