# Stock Dashboard Structure v3.0

**Date:** 2025-12-07
**Status:** ✅ Reorganized (Phase 0.3 Complete)

## Directory Tree

```
stock_dashboard/
├── DATA/                           # All data in one place (1.1GB total)
│   ├── raw/                       # Raw data from sources (253MB)
│   │   ├── ohlcv/                # Price data from APIs
│   │   ├── fundamental/          # Financial statements (Material Q3)
│   │   ├── commodity/            # Commodity prices
│   │   ├── macro/                # Interest rates, FX
│   │   ├── news/                 # News articles
│   │   └── forecast/             # BSC Excel data
│   ├── processed/                # Calculated results (834MB)
│   │   ├── fundamental/          # Financial metrics by entity
│   │   ├── technical/            # Technical indicators
│   │   ├── valuation/            # PE/PB valuations
│   │   ├── commodity/            # Processed commodity data
│   │   └── macro/                # Processed macro data
│   ├── metadata/                 # Registries (864KB)
│   │   ├── metric_registry.json  # 2,099 metrics
│   │   └── sector_industry_registry.json  # 457 tickers
│   ├── schemas/                  # Data schemas
│   │   ├── fundamental.json
│   │   ├── technical.json
│   │   ├── ohlcv.json
│   │   └── valuation.json
│   └── archive/                  # Quarterly backups
│
├── PROCESSORS/                   # All processing logic
│   ├── core/                     # Shared utilities
│   │   ├── config/               # paths.py, settings.py
│   │   ├── shared/               # Common functions
│   │   ├── formatters/           # OHLCV formatters/validators
│   │   └── registries/           # Metric/sector lookups
│   ├── fundamental/              # Financial analysis
│   │   ├── formulas/             # Pure calculation formulas (Week 3)
│   │   ├── calculators/          # Data loading + orchestration
│   │   └── pipelines/            # Quarterly update pipeline
│   ├── technical/                # Technical analysis
│   │   ├── ohlcv/                # Price data processing
│   │   ├── indicators/           # Technical indicators
│   │   ├── commodity/            # Commodity processing
│   │   ├── macro/                # Macro processing
│   │   └── pipelines/            # Daily pipelines
│   ├── valuation/                # Valuation models
│   │   ├── calculators/          # PE/PB calculators
│   │   └── pipelines/            # Valuation pipelines
│   ├── news/                     # News processing
│   └── forecast/                 # BSC forecast processing
│
├── WEBAPP/                       # Streamlit dashboard
│   ├── main.py                   # Entry point (renamed from main_app.py)
│   ├── config/                   # App configuration
│   ├── core/                     # Core app logic
│   ├── domains/                  # Domain loaders
│   ├── pages/                    # Dashboard pages
│   ├── components/               # UI components
│   ├── features/                 # Business logic
│   └── services/                 # External services
│
├── CONFIG/                       # System configuration
│   ├── schemas/
│   │   ├── master_schema.json    # Global settings
│   │   └── display/              # UI schemas
│   ├── data_sources.json
│   └── schema_registry.py
│
├── MCP/                          # AI services (if exists)
│   ├── mongodb/                  # MongoDB MCP server
│   └── local/                    # Local MCP server
│
├── mongodb/                      # MongoDB integration
├── scripts/                      # Utility scripts
├── logs/                         # Centralized logs
│   ├── processors/               # Processing logs
│   ├── webapp/                   # Webapp logs
│   └── mcp/                      # MCP logs
├── archive/                      # Deprecated code
└── docs/                         # Documentation
```

## Key Changes from v2.0

### Data Organization
- ✅ **Before:** data_warehouse/ + calculated_results/ (scattered)
- ✅ **After:** DATA/ (centralized, 1.1GB)
  - raw/ (253MB)
  - processed/ (834MB)
  - metadata/ (864KB)
  - schemas/ (consolidated)

### Processing Organization
- ✅ **Before:** data_processor/ (mixed logic)
- ✅ **After:** PROCESSORS/ (clean separation)
  - core/ → shared utilities
  - fundamental/calculators/ → Phase 0.2 calculators
  - formulas/ → To be extracted (Week 3)

### Naming Changes
- ✅ streamlit_app/ → WEBAPP/
- ✅ main_app.py → main.py
- ✅ mcp_server/ → MCP/ (if exists)
- ✅ Bsc_forecast/ → forecast/

### File Renaming
- ✅ company_financial_calculator.py → company_calculator.py
- ✅ bank_financial_calculator.py → bank_calculator.py
- ✅ insurance_financial_calculator.py → insurance_calculator.py
- ✅ security_financial_calculator.py → security_calculator.py

## Centralized Paths

All paths now accessible from:
```python
from PROCESSORS.core.config.paths import (
    DATA_ROOT,
    RAW_DATA,
    PROCESSED_DATA,
    METRIC_REGISTRY,
    SECTOR_REGISTRY,
)
```

## Next Steps (Week 2-4)

### Week 2: Formula Extraction
- Extract 155+ formulas from calculators
- Create formulas/*.py with pure functions
- Add type hints + docstrings

### Week 3: Parquet Pipeline
- Create quarterly_pipeline.py
- Automated parquet generation
- Validation reports

### Week 4: Documentation
- Create docs/INDEX.md
- Update CLAUDE.md
- Migration guide v2.0 → v3.0

## Status

- ✅ Week 1 Complete: Data reorganization
- 🔄 Week 2 Pending: Processing reorganization
- ⏳ Week 3 Pending: Formula optimization
- ⏳ Week 4 Pending: Documentation

**Last Updated:** 2025-12-07
