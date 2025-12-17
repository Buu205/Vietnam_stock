# PROCESSORS - Core Data Processing

Xử lý dữ liệu tài chính và kỹ thuật.
Core data processing modules for financial and technical analysis.

---

## 📁 Structure

```
PROCESSORS/
├── pipelines/              # Daily update orchestration
│   ├── run_all_daily_updates.py   # Master orchestrator
│   ├── README.md                  # Pipeline documentation
│   └── daily/                     # Individual daily scripts
│       ├── daily_ohlcv_update.py      # Step 1: OHLCV data fetch
│       ├── daily_ta_complete.py       # Step 2: Full TA pipeline
│       ├── daily_macro_commodity.py   # Step 3: Macro & commodity
│       ├── daily_valuation.py         # Step 4: Stock valuation
│       ├── daily_sector_analysis.py   # Step 5: Sector analysis
│       ├── daily_bsc_forecast.py      # Step 6: BSC forecast
│       └── DAILY_PIPELINE_SUMMARY.md
│
├── core/                   # Shared utilities & infrastructure
│   ├── config/             # Path configuration
│   │   └── paths.py        # Centralized path definitions
│   ├── formatters/         # Data formatters
│   │   ├── ohlcv_formatter.py
│   │   └── ohlcv_validator.py
│   ├── shared/             # Common utilities
│   │   ├── unified_mapper.py      # ✅ Unified ticker mapping
│   │   ├── symbol_loader.py       # ✅ Symbol loading utilities
│   │   ├── data_source_manager.py # ✅ Data source management
│   │   ├── data_validator.py      # ✅ Data validation
│   │   ├── date_formatter.py      # ✅ Date formatting
│   │   ├── backup_logger.py       # ✅ Backup logging
│   │   └── consistency_checker.py # ✅ Data consistency checks
│   ├── validators/         # Input/output validation
│   │   ├── input_validator.py
│   │   ├── output_validator.py
│   │   └── bsc_csv_adapter.py
│   └── ai/                 # AI-powered formula generation (experimental)
│       ├── formula_ai_assistant.py
│       ├── nlp_formula_parser.py
│       ├── metric_registry_resolver.py
│       └── formula_code_generator.py
│
├── fundamental/            # Financial metrics calculators
│   ├── calculators/        # Entity-specific calculators
│   │   ├── run_all_calculators.py  # ✅ Unified calculator (MAIN FILE)
│   │   └── __init__.py
│   ├── formulas/           # Pure calculation functions
│   │   ├── _base_formulas.py   # Common formulas (ROE, ROA, etc.)
│   │   ├── bank_formulas.py    # Bank-specific formulas
│   │   ├── company_formulas.py # Company-specific formulas
│   │   ├── registry.py         # Formula registry
│   │   └── utils.py            # safe_divide, to_percentage
│   └── csv_to_full_parquet.py  # CSV → Parquet conversion
│
├── technical/              # Technical analysis indicators
│   ├── indicators/         # TA processors
│   │   ├── technical_processor.py  # Main TA processor
│   │   ├── alert_detector.py       # Alert detection
│   │   ├── money_flow.py           # Individual money flow
│   │   ├── sector_money_flow.py    # Sector money flow
│   │   ├── sector_breadth.py       # Sector breadth
│   │   ├── market_regime.py        # Market regime detection
│   │   └── vnindex_analyzer.py     # VN-Index analysis
│   ├── ohlcv/              # OHLCV data management
│   │   └── ohlcv_daily_updater.py  # Daily OHLCV update
│   └── macro_commodity/    # Macro/commodity data
│       └── macro_commodity_fetcher.py
│
├── valuation/              # Valuation metrics
│   ├── calculators/        # PE/PB/EV-EBITDA calculators
│   │   ├── historical_pe_calculator.py
│   │   ├── historical_pb_calculator.py
│   │   ├── historical_ev_ebitda_calculator.py
│   │   ├── vnindex_valuation_calculator.py
│   │   └── run_full_backfill.py    # One-time backfill script
│   └── formulas/           # Valuation formulas
│       ├── valuation_formulas.py
│       └── metric_mapper.py
│
├── sector/                 # Sector aggregation & scoring
│   ├── calculators/        # Sector aggregators
│   │   ├── fa_aggregator.py    # Fundamental aggregation
│   │   ├── ta_aggregator.py    # Technical aggregation
│   │   ├── base_aggregator.py  # Base class
│   │   └── metric_mappings.py  # Metric definitions
│   ├── scoring/            # Scoring logic
│   │   ├── fa_scorer.py        # FA scoring
│   │   ├── ta_scorer.py        # TA scoring
│   │   └── signal_generator.py # Buy/Sell/Hold signals
│   ├── sector_processor.py     # Main orchestrator
│   └── test_scoring.py         # Test script
│
├── forecast/               # BSC Forecast processing
│   ├── bsc_forecast_processor.py  # ✅ Main processor (Excel → Parquet)
│   └── update_bsc_excel.py        # ✅ Re-read Excel script
│
└── decision/               # Trading decisions (experimental)
    └── valuation_ta_decision.py   # ⚠️ Legacy, needs update
```

---

## ⚠️ Legacy Files (Not in Active Use)

These files are kept for reference but are **not part of active pipelines**:

| File | Reason | Action |
|------|--------|--------|
| `core/shared/analyze_missing_quarters.py` | One-time fix script, uses old paths | Keep as reference |
| `core/shared/database_migrator.py` | Old migration script | Keep as reference |
| `core/shared/merge_from_copy.py` | One-time merge script | Keep as reference |
| `core/shared/restore_missing_quarters.py` | One-time fix script | Keep as reference |
| `core/shared/restore_missing_quarters_bank_security.py` | One-time fix script | Keep as reference |
| `valuation/bsc_data_processor.py` | Replaced by `forecast/bsc_forecast_processor.py` | Can delete |
| `decision/valuation_ta_decision.py` | Uses old import paths, experimental | Needs update |
| `fundamental/sector_fa_analyzer.py` | Duplicates `sector/` functionality | Can delete |

---

## 🚀 Daily Updates

**One command to update all data:**

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Pipeline Order:**
1. **OHLCV** - Market data from vnstock
2. **TA** - Technical indicators, alerts, breadth, money flow
3. **Macro** - Macro-economic & commodity data
4. **Valuation** - Individual stock PE/PB/EV-EBITDA + VN-Index
5. **Sector** - Sector aggregation & scoring
6. **BSC Forecast** - Update current prices for forecast

**Skip specific steps:**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta
```

**Run only one step:**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation
```

---

## 🔧 Module Descriptions

### pipelines/
Daily data update scripts consolidated in one place:
- `run_all_daily_updates.py` - Master orchestrator with progress tracking
- `daily/` - Individual scripts (can be run standalone)

### core/
Shared utilities and infrastructure:
- `config/paths.py` - Centralized path definitions
- `shared/unified_mapper.py` - Unified ticker/sector mapping
- `shared/symbol_loader.py` - Load symbols from metadata
- `validators/` - Input/output validation
- `ai/` - AI-powered formula generation (experimental)

### fundamental/
Financial metrics calculation:
- **`calculators/run_all_calculators.py`** - Main file with all entity calculators
- **formulas/** - Pure functions for metrics (ROE, ROA, NIM, etc.)

**Key Formulas (Bank):**
- LDR Pure = BBS_161 / BBS_330 × 100
- LDR Regulated = (BBS_160 + BNOT_13_1_1_3) / (BBS_330 + BBS_360) × 100
- CASA Ratio = (BNOT_26_1 + BNOT_26_3 + BNOT_26_5) / BNOT_26 × 100
- NPL = BNOT_4_3 + BNOT_4_4 + BNOT_4_5
- LLCR = abs(BBS_169) / NPL × 100

**Output:** `DATA/processed/fundamental/{entity_type}/{entity_type}_financial_metrics.parquet`

### technical/
Technical analysis processing:
- **indicators/** - TA processors (MA, RSI, MACD, alerts, breadth, money flow)
- **ohlcv/** - OHLCV data management classes
- **macro_commodity/** - Macro-economic & commodity data fetchers

**Output:** `DATA/processed/technical/`

### valuation/
Valuation metrics calculation:
- **calculators/** - PE, PB, EV/EBITDA calculators (individual + VNINDEX)
- **formulas/** - Valuation calculation functions

**Output:** `DATA/processed/valuation/`

### sector/
Sector-level aggregation and scoring:
- **calculators/** - FA & TA aggregators
- **scoring/** - Scoring logic (FA scores, TA scores, combined signals)
- **sector_processor.py** - Main sector analysis orchestrator

**Output:** `DATA/processed/sector/`

### forecast/
BSC Research forecast processing:
- **bsc_forecast_processor.py** - Convert Excel → Parquet (run when BSC updates Excel)
- **update_bsc_excel.py** - Script to re-read Excel file

**Output:** `DATA/processed/forecast/bsc/`

---

## 📊 Data Flow

```
RAW DATA (DATA/raw/)
    │
    ├── ohlcv/OHLCV_mktcap.parquet
    ├── fundamental/csv/Q*/
    └── commodity/, macro/

        ↓ PROCESSORS (calculations)

PROCESSED DATA (DATA/processed/)
    │
    ├── fundamental/{entity}/*_financial_metrics.parquet
    ├── technical/basic_data.parquet, alerts/, breadth/
    ├── valuation/pe/, pb/, ev_ebitda/, vnindex/
    ├── sector/sector_*.parquet
    ├── macro_commodity/macro_commodity_unified.parquet
    └── forecast/bsc/*.parquet

        ↓ WEBAPP (Streamlit visualization)
```

---

## 🧪 Testing Individual Modules

```bash
# Run all fundamental calculators
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

# Run specific entity
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank

# Test technical indicators
python3 PROCESSORS/technical/indicators/technical_processor.py

# Test valuation calculators
python3 PROCESSORS/valuation/calculators/historical_pe_calculator.py

# Test sector processor
python3 PROCESSORS/sector/sector_processor.py

# Re-read BSC Excel (when BSC updates forecast)
python3 PROCESSORS/forecast/update_bsc_excel.py
```

---

## 📝 Development Notes

### Adding New Metrics
1. Add formula to `fundamental/formulas/` or `valuation/formulas/`
2. Update calculator in `fundamental/calculators/run_all_calculators.py`
3. Update schema in `config/schema_registry/`
4. Update daily script if needed

### Adding New Indicators
1. Create indicator class in `technical/indicators/`
2. Add to TA pipeline in `technical/indicators/technical_processor.py`
3. Update `pipelines/daily/daily_ta_complete.py` if needed

### Adding New Sector Metrics
1. Update aggregators in `sector/calculators/`
2. Update scoring logic in `sector/scoring/`
3. Test with `pipelines/daily/daily_sector_analysis.py`

---

**Author:** Claude Code
**Last Updated:** 2025-12-17
**Version:** 2.0.0
