# 🎯 COMPREHENSIVE REORGANIZATION PLAN
## Stock Dashboard - Professional Structure & Pre-MCP Preparation

**Created:** 2025-12-07
**Status:** 🔴 **CRITICAL - Execute Before MCP Phase**
**Priority:** Phase 0.3 (Pre-MCP Foundation)

---

## 📋 EXECUTIVE SUMMARY

### What This Plan Covers

This comprehensive plan addresses:

1. **✅ Completed (v2.0.0):**
   - Schema consolidation framework (`/config/schemas/`)
   - Technical debt removal (`/archive/`)
   - Centralized logs (`/logs/`)
   - Package structure (`__init__.py` files)
   - Flattened technical directory

2. **🎯 This Plan (Phase 0.3 - Pre-MCP):**
   - **Professional folder restructuring** - Data vs Processing separation
   - **Formula optimization phase** - Before MCP integration
   - **Parquet generation pipeline** - Standardized outputs
   - **Complete documentation consolidation**

3. **➡️ Next Phase (Phase 1+ - MCP):**
   - MCP server integration (covered in separate docs)

---

## 🏗️ PROPOSED PROFESSIONAL STRUCTURE

### Current Problems

```
❌ Data scattered in 2 top-level folders (data_warehouse + calculated_results)
❌ Processing scripts mixed in data_processor (680+ files, no clear separation)
❌ Raw data (335MB) mixed with metadata
❌ Calculated results (834MB) not clearly separated from schemas
❌ Formula/logic embedded in calculators (hard to audit/optimize)
```

### Proposed Structure: Data-Processing Separation

```
stock_dashboard/
│
├── 📊 DATA/                                    🆕 NEW - All data in one place
│   ├── raw/                                    🔄 Move from data_warehouse/raw/
│   │   ├── ohlcv/                             ✅ Price data from APIs
│   │   │   └── OHLCV_mktcap.parquet          (164MB)
│   │   ├── fundamental/                       ✅ Financial statements
│   │   │   └── processed/                     (Material Q3 files)
│   │   │       ├── COMPANY_INCOME.csv
│   │   │       ├── BANK_INCOME.csv
│   │   │       ├── INSURANCE_INCOME.csv
│   │   │       └── SECURITY_INCOME.csv
│   │   ├── commodity/                         ✅ Commodity prices
│   │   ├── macro/                             ✅ Interest rates, FX
│   │   ├── news/                              ✅ News articles
│   │   └── forecast/                          ✅ BSC Excel data
│   │
│   ├── processed/                              🔄 Move from calculated_results/
│   │   ├── fundamental/                       (843MB total)
│   │   │   ├── company/
│   │   │   │   └── company_financial_metrics.parquet
│   │   │   ├── bank/
│   │   │   │   └── bank_financial_metrics.parquet
│   │   │   ├── insurance/
│   │   │   │   └── insurance_financial_metrics.parquet
│   │   │   └── security/
│   │   │       └── security_financial_metrics.parquet
│   │   ├── technical/                         (791MB)
│   │   │   ├── basic_data.parquet
│   │   │   ├── moving_averages.parquet
│   │   │   ├── rsi.parquet
│   │   │   ├── macd.parquet
│   │   │   ├── bollinger_bands.parquet
│   │   │   └── market_breadth.parquet
│   │   ├── valuation/                         (31MB)
│   │   │   ├── stock_pe_pb.parquet
│   │   │   ├── vnindex_pe_daily.parquet
│   │   │   └── sector_pe.parquet
│   │   ├── commodity/
│   │   └── macro/
│   │
│   ├── metadata/                               🔄 Move from data_warehouse/metadata/
│   │   ├── metric_registry.json              ✅ 2,099 metrics (752KB)
│   │   ├── sector_industry_registry.json     ✅ 457 tickers (94.5KB)
│   │   ├── ticker_details.json               ✅ Source data
│   │   └── entity_statistics.json            ✅ Entity stats
│   │
│   ├── schemas/                                🔄 Move from config/schemas/data/
│   │   ├── fundamental.json                  🆕 Consolidated
│   │   ├── technical.json                    🆕 Consolidated
│   │   ├── ohlcv.json                        🆕 Consolidated
│   │   └── valuation.json                    🆕 Consolidated
│   │
│   └── archive/                                🆕 Quarterly backups
│       ├── 2025_Q3/                          🆕 Previous quarter data
│       └── 2025_Q4/                          🆕 Current quarter backup
│
├── 🔧 PROCESSORS/                              🆕 NEW - All processing logic
│   ├── core/                                   🔄 Move from data_processor/core/
│   │   ├── __init__.py
│   │   ├── config/                            🆕 Processing configuration
│   │   │   ├── paths.py                      🆕 Centralized paths (DATA_ROOT, etc.)
│   │   │   ├── settings.py                   🆕 Processing settings
│   │   │   └── database.yaml                 🆕 DB connection configs
│   │   ├── shared/                            🆕 Shared utilities
│   │   │   ├── base_calculator.py            ✅ Phase 0.2 base class
│   │   │   ├── unified_mapper.py             ✅ Ticker → Entity mapping
│   │   │   ├── date_formatter.py             ✅ Date handling
│   │   │   ├── data_validator.py             ✅ Validation logic
│   │   │   └── backup_logger.py              ✅ Backup tracking
│   │   ├── formatters/                        🆕 Display formatters
│   │   │   ├── ohlcv_formatter.py            ✅ OHLCV display
│   │   │   ├── ohlcv_validator.py            ✅ OHLCV validation
│   │   │   └── metric_formatter.py           🆕 Metric formatting
│   │   └── registries/                        🆕 Registry lookups
│   │       ├── metric_lookup.py              ✅ Metric registry
│   │       ├── sector_lookup.py              ✅ Sector registry
│   │       └── build_registries.py           🆕 Registry builders
│   │
│   ├── fundamental/                            🔄 Reorganized
│   │   ├── __init__.py
│   │   ├── formulas/                          🆕 NEW - Extracted formulas
│   │   │   ├── __init__.py
│   │   │   ├── company_formulas.py           🆕 ROE, ROA, margins
│   │   │   ├── bank_formulas.py              🆕 NIM, NPL, CIR
│   │   │   ├── insurance_formulas.py         🆕 Combined ratio
│   │   │   └── security_formulas.py          🆕 Brokerage metrics
│   │   ├── calculators/                       🔄 Move from base/
│   │   │   ├── __init__.py
│   │   │   ├── base_financial_calculator.py  ✅ Phase 0.2
│   │   │   ├── company_calculator.py         ✅ Phase 0.2
│   │   │   ├── bank_calculator.py            ✅ Phase 0.2
│   │   │   ├── insurance_calculator.py       ✅ Phase 0.2
│   │   │   └── security_calculator.py        ✅ Phase 0.2
│   │   └── pipelines/                         🆕 Orchestration
│   │       ├── fundamental_update.py         🆕 Run all calculators
│   │       └── quarterly_pipeline.py         🆕 Full quarterly update
│   │
│   ├── technical/                              🔄 Already flattened (v2.0)
│   │   ├── __init__.py
│   │   ├── ohlcv/                             ✅ Price data processing
│   │   │   ├── __init__.py
│   │   │   └── ohlcv_updater.py
│   │   ├── indicators/                        ✅ Technical indicators
│   │   │   ├── __init__.py
│   │   │   ├── technical_processor.py
│   │   │   ├── market_breadth_processor.py
│   │   │   └── ma_screening_processor.py
│   │   ├── commodity/                         ✅ Commodity processing
│   │   ├── macro/                             ✅ Macro processing
│   │   └── pipelines/                         🆕 Orchestration
│   │       ├── daily_ohlcv_update.py         🔄 Move from parent
│   │       ├── daily_macro_commodity_update.py 🔄 Move from parent
│   │       └── daily_full_technical_pipeline.py ✅ Already exists
│   │
│   ├── valuation/                              🔄 Keep structure
│   │   ├── __init__.py
│   │   ├── calculators/                       🔄 Reorganize
│   │   │   ├── pe_pb_calculator.py
│   │   │   ├── vnindex_pe_calculator.py
│   │   │   └── sector_pe_calculator.py
│   │   └── pipelines/
│   │       └── daily_full_valuation_pipeline.py ✅ Already exists
│   │
│   ├── news/                                   ✅ Keep as-is
│   │   ├── __init__.py
│   │   └── news_pipeline.py
│   │
│   └── forecast/                               🔄 Rename from Bsc_forecast
│       ├── __init__.py
│       └── bsc_forecast_updater.py            🔄 Rename
│
├── 🎨 WEBAPP/                                  🔄 Rename from streamlit_app
│   ├── __init__.py
│   ├── main.py                                 🔄 Rename from main_app.py
│   ├── config/                                 🆕 App configuration
│   │   ├── __init__.py
│   │   ├── paths.py                           🆕 DATA_ROOT access
│   │   ├── theme.py                           🆕 UI theme settings
│   │   └── display_settings.py                🆕 Display rules
│   ├── core/                                   ✅ Keep (good structure)
│   ├── domains/                                ✅ Keep (good structure)
│   ├── pages/                                  🔄 Split large files
│   ├── components/                             ✅ Keep + expand
│   ├── features/                               ✅ Keep
│   ├── charts/                                 ✅ Keep
│   ├── services/                               ✅ Keep
│   └── ai/                                     ✅ Keep
│
├── 📊 CONFIG/                                  🔄 Simplified
│   ├── schemas/                                🔄 Keep only master + display
│   │   ├── master_schema.json                ✅ Global settings
│   │   └── display/                           ✅ UI schemas
│   │       ├── formatting_rules.json
│   │       ├── color_theme.json
│   │       └── chart_defaults.json
│   ├── data_sources.json                      ✅ Keep
│   ├── frequency_filtering_rules.json         ✅ Keep
│   └── schema_registry.py                     ✅ Keep
│
├── 🔌 MCP/                                     🔄 Rename from mcp_server
│   ├── __init__.py
│   ├── mongodb/                                🔄 Reorganize
│   │   ├── server.py
│   │   ├── handlers/
│   │   └── queries.py
│   └── local/                                  🔄 Reorganize
│       ├── server.py
│       └── handlers/
│
├── 💾 MONGODB/                                 ✅ Keep
│   ├── __init__.py
│   ├── uploader.py
│   └── queries.py
│
├── 📝 DOCS/                                    🔄 Consolidate
│   ├── INDEX.md                                🆕 Main entry point
│   ├── GETTING_STARTED.md                     🆕 Quick start guide
│   ├── CURRENT_STATUS.md                      🆕 Consolidated status
│   ├── phases/                                 🆕 Phase documentation
│   │   ├── phase_0.2_complete.md             🔄 Phase 0.2 summary
│   │   ├── phase_0.3_plan.md                 🆕 THIS PLAN
│   │   └── phase_1_mcp_plan.md               🔄 MCP roadmap
│   ├── architecture/                           ✅ Keep (archive old)
│   │   ├── CURRENT_ARCHITECTURE.md           🆕 Up-to-date architecture
│   │   ├── DATA_FLOW.md                      🆕 Data flow diagram
│   │   └── archive/                           🔄 Old docs
│   └── mcp/                                    🔄 Move from mongodb_mcp
│       ├── INDEX.md
│       ├── SETUP.md
│       └── TROUBLESHOOTING.md
│
├── 📜 SCRIPTS/                                 ✅ Keep
│   └── utilities/
│
├── 📁 LOGS/                                    ✅ Keep (v2.0)
│   ├── processors/                             ✅ All processing logs
│   ├── webapp/                                 🆕 Streamlit logs
│   └── mcp/                                    ✅ MCP logs
│
└── 🗄️ ARCHIVE/                                ✅ Keep (v2.0)
    └── deprecated_v1.0/                        ✅ Old code

```

---

## 🎯 PHASE 0.3: PRE-MCP FOUNDATION

### Overview

**Timeline:** 3-4 weeks
**Goal:** Professional structure + Formula optimization + Complete documentation

**Why Before MCP?**
- MCP servers need clean data access paths
- Formula optimization ensures MCP gets quality data
- Professional structure makes MCP integration easier

---

## 📅 DETAILED ROADMAP

### WEEK 1: Data Reorganization (5 days)

#### Day 1-2: Create New Structure
```bash
# 1. Create DATA/ directory structure
mkdir -p DATA/{raw,processed,metadata,schemas,archive}
mkdir -p DATA/raw/{ohlcv,fundamental/processed,commodity,macro,news,forecast}
mkdir -p DATA/processed/{fundamental,technical,valuation,commodity,macro}
mkdir -p DATA/processed/fundamental/{company,bank,insurance,security}

# 2. Create PROCESSORS/ directory structure
mkdir -p PROCESSORS/{core,fundamental,technical,valuation,news,forecast}
mkdir -p PROCESSORS/core/{config,shared,formatters,registries}
mkdir -p PROCESSORS/fundamental/{formulas,calculators,pipelines}
mkdir -p PROCESSORS/technical/pipelines
mkdir -p PROCESSORS/valuation/{calculators,pipelines}
```

#### Day 3: Move Raw Data
```bash
# Move raw data: data_warehouse/raw/ → DATA/raw/
rsync -av data_warehouse/raw/ DATA/raw/

# Move metadata: data_warehouse/metadata/ → DATA/metadata/
rsync -av data_warehouse/metadata/ DATA/metadata/

# Verify (should match)
du -sh data_warehouse/raw DATA/raw
du -sh data_warehouse/metadata DATA/metadata
```

#### Day 4: Move Processed Data
```bash
# Move calculated results: calculated_results/ → DATA/processed/
rsync -av calculated_results/fundamental/ DATA/processed/fundamental/
rsync -av calculated_results/technical/ DATA/processed/technical/
rsync -av calculated_results/valuation/ DATA/processed/valuation/
rsync -av calculated_results/commodity/ DATA/processed/commodity/
rsync -av calculated_results/macro/ DATA/processed/macro/

# Verify total size (should be ~843MB)
du -sh DATA/processed
```

#### Day 5: Update Schemas & Paths
```bash
# Consolidate schemas
# Merge: calculated_results/schemas/*.json → DATA/schemas/
python3 PROCESSORS/core/registries/consolidate_schemas.py

# Create centralized paths configuration
# File: PROCESSORS/core/config/paths.py
```

**Deliverables Week 1:**
- ✅ Complete DATA/ structure with 335MB + 843MB data
- ✅ All raw data in DATA/raw/
- ✅ All processed data in DATA/processed/
- ✅ Consolidated schemas in DATA/schemas/
- ✅ Centralized paths.py configuration

---

### WEEK 2: Processing Reorganization (5 days)

#### Day 1: Move Core Utilities
```bash
# Move: data_processor/core/ → PROCESSORS/core/shared/
rsync -av data_processor/core/ PROCESSORS/core/shared/

# Reorganize into subdirectories
mv PROCESSORS/core/shared/ohlcv_*.py PROCESSORS/core/formatters/
mv PROCESSORS/core/shared/metric_lookup.py PROCESSORS/core/registries/
mv PROCESSORS/core/shared/sector_lookup.py PROCESSORS/core/registries/
mv PROCESSORS/core/shared/build_*.py PROCESSORS/core/registries/
```

#### Day 2: Reorganize Fundamental Processors
```bash
# Move: data_processor/fundamental/base/ → PROCESSORS/fundamental/calculators/
rsync -av data_processor/fundamental/base/ PROCESSORS/fundamental/calculators/

# Rename files for clarity
cd PROCESSORS/fundamental/calculators
mv company_financial_calculator.py company_calculator.py
mv bank_financial_calculator.py bank_calculator.py
mv insurance_financial_calculator.py insurance_calculator.py
mv security_financial_calculator.py security_calculator.py
```

#### Day 3: Extract Formulas (NEW - Phase 0.3)
```python
# Create: PROCESSORS/fundamental/formulas/company_formulas.py
"""
Extracted formulas from company_calculator.py

Separation of concerns:
- formulas/*.py: Pure calculation logic (testable, auditable)
- calculators/*.py: Data loading, orchestration, output
"""

class CompanyFormulas:
    """Pure calculation functions for company metrics"""

    @staticmethod
    def calculate_roe(net_profit: float, total_equity: float) -> float:
        """ROE = (Net Profit / Total Equity) × 100"""
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return (net_profit / total_equity) * 100

    @staticmethod
    def calculate_roa(net_profit: float, total_assets: float) -> float:
        """ROA = (Net Profit / Total Assets) × 100"""
        if total_assets == 0 or pd.isna(total_assets):
            return None
        return (net_profit / total_assets) * 100

    @staticmethod
    def calculate_gross_margin(gross_profit: float, revenue: float) -> float:
        """Gross Margin = (Gross Profit / Revenue) × 100"""
        if revenue == 0 or pd.isna(revenue):
            return None
        return (gross_profit / revenue) * 100

    # ... (all 50+ company formulas extracted)
```

**Why Extract Formulas?**
1. ✅ **Easier to audit** - All formulas in one place
2. ✅ **Easier to optimize** - Change formula without touching calculator
3. ✅ **Easier to test** - Unit test each formula independently
4. ✅ **Documentation** - Clear formula definitions for MCP
5. ✅ **Reusability** - Use same formulas in different contexts

#### Day 4: Reorganize Technical Processors
```bash
# Move pipeline files to pipelines/
mv PROCESSORS/technical/daily_*.py PROCESSORS/technical/pipelines/
```

#### Day 5: Update All Import Paths
```python
# Create migration script: scripts/update_imports.py
# Updates all imports:
# - data_processor → PROCESSORS
# - data_warehouse/raw → DATA/raw
# - calculated_results → DATA/processed
# - streamlit_app → WEBAPP
```

**Deliverables Week 2:**
- ✅ PROCESSORS/ structure with all processing code
- ✅ Formulas extracted to separate files (50+ company formulas)
- ✅ Calculators focused on orchestration
- ✅ All imports updated
- ✅ Tests passing with new structure

---

### WEEK 3: Formula Optimization & Parquet Generation (5 days)

#### Day 1-2: Audit & Optimize Formulas

**Current State:**
```python
# Example: company_calculator.py (embedded formula)
def calculate_all_metrics(self, df):
    # 500+ lines of mixed logic
    df['roe'] = (df['CIS_62'] / df['CBS_270']) * 100
    df['roa'] = (df['CIS_62'] / df['CBS_100']) * 100
    df['gross_margin'] = (df['CIS_11'] / df['CIS_02']) * 100
    # ... 50+ more formulas mixed with data loading
```

**After Optimization:**
```python
# File: PROCESSORS/fundamental/formulas/company_formulas.py
class CompanyFormulas:
    """
    All company calculation formulas.

    Registry mapping:
    - CIS_62: net_profit (Lợi nhuận sau thuế công ty mẹ)
    - CBS_270: total_equity (Vốn chủ sở hữu)
    - CBS_100: total_assets (Tổng tài sản)
    - CIS_11: gross_profit (Lợi nhuận gộp)
    - CIS_02: revenue (Doanh thu thuần)
    """

    @staticmethod
    def calculate_roe(net_profit: float, total_equity: float) -> float:
        """
        Return on Equity (ROE)

        Formula: (Net Profit / Total Equity) × 100
        Unit: Percentage (%)
        Good range: 15-25% (Vietnam market)
        """
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return round((net_profit / total_equity) * 100, 2)

    # ... all formulas documented, typed, tested
```

**Optimization Checklist:**
- [ ] Extract all 50+ company formulas
- [ ] Extract all 40+ bank formulas (NIM, NPL, CIR, etc.)
- [ ] Extract all 30+ insurance formulas
- [ ] Extract all 35+ security formulas
- [ ] Add type hints (float, Optional[float])
- [ ] Add docstrings (formula, unit, good range)
- [ ] Add registry mapping comments (CIS_62 = net_profit)
- [ ] Add edge case handling (division by zero, None)
- [ ] Add rounding (2 decimal places)

#### Day 3-4: Create Standardized Parquet Generation Pipeline

```python
# File: PROCESSORS/fundamental/pipelines/quarterly_pipeline.py
"""
Quarterly Fundamental Data Pipeline

Flow:
1. Load raw data from DATA/raw/fundamental/processed/
2. Apply formulas from PROCESSORS/fundamental/formulas/
3. Validate using PROCESSORS/core/shared/data_validator.py1
4. Generate parquet files to DATA/processed/fundamental/
5. Create backup in DATA/archive/{year}_Q{quarter}/
6. Generate validation report
"""

class QuarterlyFundamentalPipeline:
    def __init__(self):
        self.data_root = Path("DATA")
        self.raw_path = self.data_root / "raw/fundamental/processed"
        self.output_path = self.data_root / "processed/fundamental"
        self.archive_path = self.data_root / "archive"

    def run(self, quarter: str = "2025-Q4"):
        """
        Run full quarterly update pipeline

        Args:
            quarter: Quarter identifier (e.g., "2025-Q4")

        Steps:
            1. Validate raw data
            2. Run all 4 entity calculators
            3. Validate calculated results
            4. Generate parquet files
            5. Create archive backup
            6. Generate HTML report

        Output:
            - DATA/processed/fundamental/company/company_financial_metrics.parquet
            - DATA/processed/fundamental/bank/bank_financial_metrics.parquet
            - DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
            - DATA/processed/fundamental/security/security_financial_metrics.parquet
            - DATA/archive/2025_Q4/fundamental/
            - LOGS/processors/quarterly_update_2025-12-07.html
        """

        # Step 1: Validate raw data
        validation_results = self.validate_raw_data()
        if not validation_results.is_valid:
            raise ValueError("Raw data validation failed")

        # Step 2: Run calculators in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for entity_type in ["company", "bank", "insurance", "security"]:
                calculator = self.get_calculator(entity_type)
                future = executor.submit(calculator.calculate_and_save)
                futures.append((entity_type, future))

        # Step 3: Collect results
        results = {}
        for entity_type, future in futures:
            results[entity_type] = future.result()

        # Step 4: Validate calculated results
        self.validate_calculated_results(results)

        # Step 5: Create archive
        self.create_archive_backup(quarter)

        # Step 6: Generate report
        self.generate_validation_report(results, quarter)

        return results
```

#### Day 5: Test & Validate

```bash
# Test formula extraction
python3 -m pytest PROCESSORS/fundamental/formulas/tests/

# Test pipeline
python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py --dry-run

# Run full pipeline (if validation passes)
python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py --quarter 2025-Q4
```

**Deliverables Week 3:**
- ✅ All formulas extracted & documented (155+ formulas)
- ✅ Type hints & docstrings added
- ✅ Edge cases handled
- ✅ Quarterly pipeline script created
- ✅ Parquet generation tested
- ✅ Validation reports generated

---

### WEEK 4: Documentation & Final Integration (5 days)

#### Day 1-2: Consolidate Documentation

```markdown
# Create: DOCS/INDEX.md (Main entry point)

# Stock Dashboard Documentation

## Quick Start
- [Getting Started](./GETTING_STARTED.md) - 5-minute setup guide
- [Current Status](./CURRENT_STATUS.md) - What's done, what's next

## Development Phases
- [Phase 0.2 Complete](./phases/phase_0.2_complete.md) - Base calculators
- [Phase 0.3 Plan](./phases/phase_0.3_plan.md) - Professional structure (THIS PHASE)
- [Phase 1 MCP Plan](./phases/phase_1_mcp_plan.md) - MCP integration

## Architecture
- [Current Architecture](./architecture/CURRENT_ARCHITECTURE.md) - Latest structure
- [Data Flow](./architecture/DATA_FLOW.md) - How data moves through system
- [Formula Reference](./architecture/FORMULA_REFERENCE.md) - All 155+ formulas

## MCP Integration
- [MCP Setup Guide](./mcp/SETUP.md)
- [MCP Troubleshooting](./mcp/TROUBLESHOOTING.md)

## Archive (Old Docs)
- [Archive](./architecture/archive/) - Old plans, obsolete docs
```

#### Day 3: Update CLAUDE.md

```bash
# Update: CLAUDE.md with new structure
# - Update paths (DATA/, PROCESSORS/, WEBAPP/)
# - Update import examples
# - Update command examples
# - Add formula reference section
```

#### Day 4: Create Migration Guide

```markdown
# Create: DOCS/MIGRATION_GUIDE_v2.0_to_v3.0.md

# Migration Guide: v2.0 → v3.0

## Breaking Changes

### Path Changes
- `data_warehouse/raw/` → `DATA/raw/`
- `calculated_results/` → `DATA/processed/`
- `data_processor/` → `PROCESSORS/`
- `streamlit_app/` → `WEBAPP/`

### Import Changes
```python
# Before (v2.0)
from data_processor.core.unified_mapper import UnifiedTickerMapper
from data_processor.fundamental.base.company_calculator import CompanyCalculator

# After (v3.0)
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from PROCESSORS.fundamental.calculators.company_calculator import CompanyCalculator
```

### Command Changes
```bash
# Before (v2.0)
python3 data_processor/fundamental/base/company_financial_calculator.py

# After (v3.0)
python3 PROCESSORS/fundamental/calculators/company_calculator.py
# OR use pipeline
python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py
```

## Migration Steps

1. **Backup current system**
   ```bash
   git tag v2.0-before-phase-0.3
   tar -czf backup_v2.0_$(date +%Y%m%d).tar.gz data_warehouse/ calculated_results/ data_processor/
   ```

2. **Run migration script**
   ```bash
   python3 scripts/migrate_v2_to_v3.py --dry-run
   python3 scripts/migrate_v2_to_v3.py --execute
   ```

3. **Update dependencies**
   ```bash
   # Update all imports in WEBAPP/
   python3 scripts/update_imports.py --path WEBAPP/

   # Update all imports in PROCESSORS/
   python3 scripts/update_imports.py --path PROCESSORS/
   ```

4. **Test**
   ```bash
   # Test fundamental pipeline
   python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py --dry-run

   # Test technical pipeline
   python3 PROCESSORS/technical/pipelines/daily_full_technical_pipeline.py --help

   # Test webapp
   streamlit run WEBAPP/main.py
   ```
```

#### Day 5: Final Testing & Deployment

```bash
# Full system test
./scripts/test_all.sh

# If all pass, remove old directories
rm -rf data_warehouse/ calculated_results/ data_processor/ streamlit_app/

# Update .gitignore
echo "DATA/processed/" >> .gitignore
echo "DATA/archive/" >> .gitignore
echo "LOGS/" >> .gitignore
```

**Deliverables Week 4:**
- ✅ Consolidated documentation (INDEX.md + guides)
- ✅ Updated CLAUDE.md
- ✅ Migration guide (v2.0 → v3.0)
- ✅ All tests passing
- ✅ Old directories removed
- ✅ Ready for Phase 1 (MCP)

---

## 📊 SUCCESS METRICS

### Phase 0.3 Completion Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| **Data Organization** |
| Raw data centralized | 100% in DATA/raw/ | `du -sh DATA/raw/` = 335MB |
| Processed data centralized | 100% in DATA/processed/ | `du -sh DATA/processed/` = 843MB |
| Schemas consolidated | 4 schemas | `ls DATA/schemas/*.json` |
| **Processing Organization** |
| Formulas extracted | 155+ formulas | Count in formulas/*.py |
| Calculators refactored | 4 entity types | All use formulas/*.py |
| Pipelines created | 3 pipelines | fundamental, technical, valuation |
| **Code Quality** |
| Type hints added | 100% formulas | mypy check |
| Docstrings added | 100% formulas | pydocstyle check |
| Tests passing | 100% | pytest |
| **Documentation** |
| Docs consolidated | Single INDEX.md | All linked from INDEX.md |
| Migration guide | Complete | Tested migration path |
| CLAUDE.md updated | v3.0 structure | Paths, imports, commands |

---

## 🎯 BENEFITS ACHIEVED

### For Development
- ✅ **Clear separation**: Data (DATA/) vs Processing (PROCESSORS/)
- ✅ **Easier navigation**: All formulas in formulas/*.py
- ✅ **Easier testing**: Pure functions (formulas) vs orchestration (calculators)
- ✅ **Easier auditing**: Review all 155+ formulas in one place

### For MCP Integration (Phase 1)
- ✅ **Clean data access**: MCP servers → DATA/processed/
- ✅ **Formula documentation**: MCP can explain formulas to users
- ✅ **Standardized paths**: No more searching for files
- ✅ **Quality assurance**: Validation pipeline ensures clean data

### For Maintenance
- ✅ **Optimize formulas**: Change formula without touching calculator
- ✅ **Add new metrics**: Just add to formulas/*.py
- ✅ **Debug issues**: Clear data flow (raw → formulas → processed)
- ✅ **Quarterly updates**: Single command pipeline

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking imports** | HIGH | Migration script + comprehensive testing |
| **Data loss** | CRITICAL | Full backup before migration + archive/ |
| **Formula errors** | HIGH | Extract & test formulas before refactor |
| **Path confusion** | MEDIUM | Centralized paths.py + clear documentation |
| **Team confusion** | MEDIUM | Migration guide + updated CLAUDE.md |

---

## 📅 TIMELINE SUMMARY

```
Week 1 (Dec 8-12):  Data Reorganization
├── Day 1-2: Create new structure
├── Day 3: Move raw data (335MB)
├── Day 4: Move processed data (843MB)
└── Day 5: Update schemas & paths

Week 2 (Dec 15-19): Processing Reorganization
├── Day 1: Move core utilities
├── Day 2: Reorganize fundamental processors
├── Day 3: Extract formulas (KEY INNOVATION)
├── Day 4: Reorganize technical processors
└── Day 5: Update all import paths

Week 3 (Dec 22-26): Formula Optimization & Parquet Generation
├── Day 1-2: Audit & optimize 155+ formulas
├── Day 3-4: Create quarterly pipeline
└── Day 5: Test & validate

Week 4 (Dec 29-Jan 2): Documentation & Integration
├── Day 1-2: Consolidate documentation
├── Day 3: Update CLAUDE.md
├── Day 4: Create migration guide
└── Day 5: Final testing & deployment

TOTAL: 4 weeks (~20 working days)
```

---

## 🔄 WHAT HAPPENS AFTER PHASE 0.3?

### Phase 1: MCP Integration (4 weeks)

With clean structure from Phase 0.3:

```python
# MCP Server can now easily access data
from MCP.mongodb.server import FinancialMCPServer

server = FinancialMCPServer()

@server.tool()
async def get_company_fundamentals(symbol: str):
    # Read from clean paths
    data_path = Path("DATA/processed/fundamental/company/")
    df = pd.read_parquet(data_path / "company_financial_metrics.parquet")

    # Use formula documentation
    from PROCESSORS.fundamental.formulas.company_formulas import CompanyFormulas
    formulas_doc = CompanyFormulas.get_documentation()

    # Return structured data + formula explanations
    return {
        "data": df[df['symbol'] == symbol],
        "formulas": formulas_doc,
        "metadata": {...}
    }
```

**Why Phase 0.3 Enables MCP:**
1. ✅ Clean data paths → MCP knows where to find data
2. ✅ Formula documentation → MCP can explain to users
3. ✅ Standardized parquet → MCP can query directly
4. ✅ Validation pipeline → MCP gets quality data

---

## 📚 RELATED DOCUMENTS

### Current Phase
- **[REORGANIZATION_COMPLETE_SUMMARY.md](./REORGANIZATION_COMPLETE_SUMMARY.md)** - v2.0 reorganization
- **[NEW_STRUCTURE.md](./NEW_STRUCTURE.md)** - v2.0 structure details

### Previous Phases
- **[MASTER_PLAN.md](./MASTER_PLAN.md)** - Overall roadmap
- **[DATA_STANDARDIZATION.md](./architecture/DATA_STANDARDIZATION.md)** - Phase 0.1-0.2

### Next Phase
- **[MCP Integration Plan](./phases/phase_1_mcp_plan.md)** - To be created after Phase 0.3

---

## ✅ IMMEDIATE NEXT STEPS

### This Week (Dec 8-12)

1. **Review this plan**
   - Confirm data separation strategy
   - Confirm formula extraction approach
   - Confirm timeline

2. **Start Week 1: Data Reorganization**
   - Create DATA/ structure
   - Move raw data (335MB)
   - Move processed data (843MB)
   - Update schemas

3. **Track progress**
   - Use TodoWrite to track daily tasks
   - Update this document with progress
   - Note any issues/adjustments

---

**Document Status:** 🔴 **ACTIVE PLAN**
**Last Updated:** 2025-12-07
**Next Review:** End of Week 1 (Dec 12)
**Owner:** Buu Phan

---

## 🎯 KEY INNOVATIONS IN THIS PLAN

### 1. Data-Processing Separation
- **Before:** Mixed in data_warehouse/ + calculated_results/ + data_processor/
- **After:** Clean DATA/ (read-only by MCP) + PROCESSORS/ (logic)

### 2. Formula Extraction
- **Before:** Formulas embedded in 500+ line calculators
- **After:** 155+ formulas extracted, documented, testable
- **Benefit:** Easier to audit, optimize, and explain to MCP

### 3. Standardized Pipeline
- **Before:** Manual 20-step quarterly update
- **After:** Single-command quarterly_pipeline.py
- **Benefit:** Faster, error-free, audit-ready

### 4. Documentation Consolidation
- **Before:** 30+ scattered markdown files
- **After:** Single INDEX.md entry point + clear structure
- **Benefit:** Easier for future Claude Code instances

---

**Ready to execute! 🚀**

---

## 🏢 PROFESSIONAL FOLDER NAMING CONVENTIONS

### Naming Philosophy

```
✅ Functional over Generic
   → DATA/ vs raw_data/
   → PROCESSING/ vs scripts/
   → FRONTEND/ vs ui/

✅ Descriptive over Abbreviated
   → technical_analysis/ vs ta/
   → business_metrics/ vs metrics/
   → market_data/ vs ohlcv/

✅ Consistent Suffixes
   → *_analyzer.py vs *_calc.py
   → *_pipeline.py vs *_job.py
   → *_registry.py vs *_lookup.py
```

### Proposed Professional Names for Financial Analysis Context

| Current Name | Proposed Professional Name | Finance Context Rationale |
|--------------|---------------------------|---------------------------|
| DATA/ | DATA_LAKE/ | Central repository for all financial data |
| raw/ | market_sources/ | External data sources for market data |
| processed/ | processed_analytics/ | Financial data after analysis & calculations |
| metadata/ | reference_data/ | Reference data for financial calculations |
| PROCESSORS/ | ANALYTICS_TEAM/ | Team performing financial analysis |
| core/ | core_services/ | Core services for financial analysis |
| fundamental/ | FUNDAMENTAL_ANALYSIS/ | Standard term for financial statement analysis |
| technical/ | TECHNICAL_ANALYSIS/ | Standard term for market technical analysis |
| formulas/ | FINANCIAL_METRICS/ | Formulas for financial calculations |
| calculators/ | ANALYTICS_ENGINES/ | Engines that perform financial calculations |
| WEBAPP/ | DASHBOARD/ | Financial dashboard interface |
| CONFIG/ | SYSTEM_CONFIG/ | System configuration for financial platform |
| MCP/ | AI_SERVICES/ | AI services for financial insights |
| MONGODB/ | DATA_STORE/ | Database for financial data storage |
| DOCS/ | KNOWLEDGE_BASE/ | Documentation base for financial knowledge |
| SCRIPTS/ | AUTOMATION/ | Automation for financial processes |
| LOGS/ | AUDIT_LOGS/ | Logs for financial audit trail |

### Final Professional Financial Analysis Structure

```
stock_dashboard/
├── 📁 DATA_LAKE/                           # Central repository for all financial data
│   ├── market_sources/                           # External data sources for market data
│   │   ├── price_data/                       # OHLCV data from APIs
│   │   ├── company_reports/                  # Financial statements
│   │   ├── economic_indicators/              # Commodity, macro data
│   │   ├── market_intelligence/              # News, forecasts
│   │   └── reference_data/                   # Metadata, registries
│   │
│   ├── processed_analytics/                       # Financial data after analysis & calculations
│   │   ├── fundamental_metrics/             # Calculated financial metrics
│   │   ├── technical_indicators/             # Technical analysis results
│   │   ├── valuation_models/               # PE/PB valuation models
│   │   └── risk_analytics/                 # Risk assessment metrics
│   │
│   └── historical_archives/                         # Historical backups for audit
│       └── quarterly_snapshots/
│
├── 🔧 ANALYTICS_TEAM/                      # Team performing financial analysis
│   ├── core_services/                           # Core services for financial analysis
│   │   ├── infrastructure/                 # Paths, settings, DB connections
│   │   ├── shared_utilities/               # Common functions for analysis
│   │   ├── data_formatters/                # Display formatting for financial data
│   │   └── reference_registries/             # Registry lookups for financial entities
│   │
│   ├── FUNDAMENTAL_ANALYSIS/                   # Financial statement analysis team
│   │   ├── FINANCIAL_METRICS/              # Formulas for financial calculations
│   │   ├── ANALYTICS_ENGINES/              # Engines that perform financial calculations
│   │   ├── industry_analyzers/             # Industry-specific analysis engines
│   │   │   ├── corporate_analyzer.py    # For corporations
│   │   │   ├── banking_analyzer.py       # For banks
│   │   │   ├── insurance_analyzer.py    # For insurance companies
│   │   │   └── securities_analyzer.py   # For securities firms
│   │   └── analysis_workflows/              # Orchestration of fundamental analysis
│   │
│   ├── TECHNICAL_ANALYSIS/                    # Market technical analysis team
│   │   ├── market_data_processing/        # Price data processing
│   │   ├── technical_indicators/          # Technical indicators calculation
│   │   ├── pattern_recognition/           # Chart pattern analysis
│   │   └── technical_workflows/           # Technical analysis pipelines
│   │
│   └── VALUATION_MODELS/                       # Valuation calculations
│       ├── valuation_engines/                # PE/PB calculators
│       ├── discount_models/                 # DCF, NPV models
│       └── valuation_workflows/             # Valuation analysis pipelines
│
├── 📈 DASHBOARD/                              # Financial dashboard interface
│   ├── main_application/                      # Main dashboard app
│   ├── dashboard_config/                      # Dashboard settings
│   ├── financial_components/                 # Financial UI components
│   ├── visualization_modules/               # Charts and graphs
│   └── user_features/                        # Feature modules for users
│
├── 📋 SYSTEM_CONFIG/                         # System configuration for financial platform
│   ├── data_schemas/                        # Data schemas for financial data
│   ├── source_connections/                   # Data source configurations
│   └── platform_settings/                   # Platform-wide settings
│
├── 🤖 AI_SERVICES/                          # AI services for financial insights
│   ├── mcp_financial_analyst/             # MCP server for financial analysis
│   ├── ai_insight_engines/               # AI engines for insights
│   └── automated_reporting/              # Automated report generation
│
├── 💾 DATA_STORE/                           # Database for financial data storage
│   ├── financial_database/                   # Main financial data storage
│   ├── cache_layers/                        # Redis/Memcached layers
│   └── backup_systems/                       # Backup storage systems
│
├── 📚 KNOWLEDGE_BASE/                        # Documentation base for financial knowledge
│   ├── analysis_guides/                      # Guides for financial analysis
│   ├── methodology_documentation/          # Financial analysis methodologies
│   ├── api_reference/                       # API documentation
│   └── regulatory_compliance/             # Compliance documentation
│
├── 🛠️ AUTOMATION/                           # Automation for financial processes
│   ├── data_collection/                     # Automated data collection
│   ├── report_generation/                  # Automated report generation
│   └── monitoring_alerts/                 # System monitoring
│
└── 📊 AUDIT_LOGS/                          # Logs for financial audit trail
    ├── analysis_logs/                        # Financial analysis execution logs
    ├── data_quality_logs/                   # Data quality monitoring logs
    └── system_audit_logs/                    # System access and change logs
```

### Benefits of Professional Financial Analysis Structure

```
✅ Industry-Specific Terminology
   → FUNDAMENTAL_ANALYSIS (standard term for financial statement analysis)
   → TECHNICAL_ANALYSIS (standard term for market technical analysis)
   → FINANCIAL_METRICS (clear term for financial calculation formulas)
   → DASHBOARD (industry standard for financial interfaces)

✅ Domain-Specific Organization
   → Banking analyzer separated from corporate analyzer
   → Insurance metrics isolated for industry-specific formulas
   → Securities analysis separate for broker-dealer metrics
   → Clear separation between fundamental and technical analysis

✅ Regulatory Compliance Ready
   → AUDIT_LOGS for financial audit trail
   → KNOWLEDGE_BASE for methodology documentation
   → Reference data properly maintained for regulatory review
   → Risk analysis clearly separated from other metrics

✅ Team Specialization Support
   → Fundamental analysts focus on FUNDAMENTAL_ANALYSIS/
   → Technical analysts focus on TECHNICAL_ANALYSIS/
   → Quant teams focus on FINANCIAL_METRICS/ and VALUATION_MODELS/
   → Compliance teams focus on AUDIT_LOGS/ and regulatory documentation

✅ Financial Workflow Optimization
   → Clear data flow: market_sources → processed_analytics → dashboard
   → Separated concerns: data collection, analysis, presentation
   → Scalable architecture for expanding financial product coverage
```
