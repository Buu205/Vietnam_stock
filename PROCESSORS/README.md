# PROCESSORS - Core Data Processing

Xử lý dữ liệu tài chính và kỹ thuật.
Core data processing modules for financial and technical analysis.

---

## 📁 Structure

```
PROCESSORS/
├── pipelines/          # 🆕 Daily update scripts (consolidated)
│   ├── run_all_daily_updates.py  # Master orchestrator
│   ├── daily_ohlcv_update.py     # OHLCV data fetch
│   ├── daily_ta_complete.py      # Full TA pipeline
│   ├── daily_macro_commodity.py  # Macro & commodity
│   ├── daily_valuation.py        # Stock valuation
│   └── daily_sector_analysis.py  # Sector analysis
│
├── core/               # Shared utilities & infrastructure
│   ├── shared/         # Common utilities
│   └── registries/     # Legacy (moved to config/)
│
├── fundamental/        # Financial metrics calculators
│   ├── calculators/    # Entity-specific calculators
│   │   ├── company_calculator.py
│   │   ├── bank_calculator.py
│   │   ├── insurance_calculator.py
│   │   └── security_calculator.py
│   └── formulas/       # Pure calculation functions
│
├── technical/          # Technical analysis indicators
│   ├── indicators/     # TA processors
│   ├── ohlcv/          # OHLCV data management
│   └── macro_commodity/ # Macro/commodity data
│
├── valuation/          # Valuation metrics
│   ├── calculators/    # PE/PB/EV-EBITDA calculators
│   └── formulas/       # Valuation formulas
│
└── sector/             # Sector aggregation & scoring
    ├── calculators/    # Sector aggregators
    ├── scoring/        # Scoring logic
    └── sector_processor.py  # Main orchestrator
```

---

## 🚀 Daily Updates

**One command to update all data:**

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**See detailed documentation:**
- [pipelines/README.md](pipelines/README.md)

---

## 🔧 Module Descriptions

### pipelines/
Daily data update scripts consolidated in one place. Runs in correct order:
1. OHLCV → 2. TA → 3. Macro → 4. Stock Valuation → 5. Sector Analysis

### core/
Shared utilities and infrastructure:
- `shared/unified_mapper.py` - Unified ticker mapping
- `shared/data_loader.py` - Common data loading functions

### fundamental/
Financial metrics calculation:
- **calculators/** - Entity-specific calculators (company, bank, insurance, security)
- **formulas/** - Pure functions for metrics (ROE, ROA, EPS, etc.)

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

---

## 📊 Data Flow

```
RAW DATA (DATA/raw/)
    ↓
PROCESSORS (calculations)
    ↓
PROCESSED DATA (DATA/processed/)
    ↓
WEBAPP (Streamlit visualization)
```

---

## 🧪 Testing Individual Modules

```bash
# Test fundamental calculators
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Test technical indicators
python3 PROCESSORS/technical/indicators/technical_processor.py

# Test valuation calculators
python3 PROCESSORS/valuation/calculators/historical_pe_calculator.py

# Test sector processor
python3 PROCESSORS/sector/sector_processor.py
```

---

## 📝 Development Notes

### Adding New Metrics
1. Add formula to `fundamental/formulas/` or `valuation/formulas/`
2. Update calculator in `fundamental/calculators/` or `valuation/calculators/`
3. Update schema in `config/schema_registry/`
4. Update daily script if needed

### Adding New Indicators
1. Create indicator class in `technical/indicators/`
2. Add to TA pipeline in `technical/indicators/technical_processor.py`
3. Update `pipelines/daily_ta_complete.py` if needed

### Adding New Sector Metrics
1. Update aggregators in `sector/calculators/`
2. Update scoring logic in `sector/scoring/`
3. Test with `pipelines/daily_sector_analysis.py`

---

**Author:** Claude Code
**Last Updated:** 2025-12-15
**Version:** 1.0.0
