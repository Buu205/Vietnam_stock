# 🏗️ REORGANIZATION MASTER PLAN - Stock Dashboard Architecture

**Goal:** Transform from scattered structure to clean, scalable architecture
**Status:** Planning Phase
**Priority:** 🔴 CRITICAL - Do BEFORE Phase 0.2

---

## 🎯 WHY REORGANIZE NOW?

### Current Problems (from ARCHITECTURE_ANALYSIS.md)
1. ❌ **Schema scattered**: 10 schema files in 3 locations
2. ❌ **Technical debt**: `/copy` folder with 100% duplicate code
3. ❌ **Nested chaos**: `technical/technical/` confusing structure
4. ❌ **Import hell**: 40+ files with `sys.path` hacks
5. ❌ **Log pollution**: Log files in root directory
6. ❌ **Missing packages**: Only 9 `__init__.py` files (should have 30-35)
7. ❌ **Monolithic files**: Pages with 1,200-2,140 LOC

### Why Before Phase 0.2?
- Phase 0.2 creates `BaseFinancialCalculator` → Need clean structure first
- Schema consolidation requires new `/config/schemas/` location
- Refactoring calculators easier with proper package structure
- Future phases (MCP, API) need solid foundation

---

## 📐 TARGET ARCHITECTURE

### Proposed Structure (Hybrid Approach)

**We KEEP current top-level structure BUT reorganize internals:**

```
stock_dashboard/
├── config/                              ✅ KEEP + EXPAND
│   ├── schemas/                         🆕 NEW - Central schemas
│   │   ├── master_schema.json          ✅ Created
│   │   ├── data/                       🆕 Consolidated data schemas
│   │   │   ├── fundamental.json
│   │   │   ├── technical.json
│   │   │   ├── ohlcv.json
│   │   │   └── valuation.json
│   │   ├── display/                    🆕 UI schemas
│   │   │   ├── formatting_rules.json
│   │   │   ├── color_theme.json
│   │   │   └── chart_defaults.json
│   │   └── metadata/                   🔗 Symlinks
│   │       ├── metric_registry.json → /data_warehouse/metadata/
│   │       └── sector_registry.json → /data_warehouse/metadata/
│   ├── database.yaml                   🆕 Database config
│   ├── data_sources.json              ✅ Existing
│   └── settings.py                     🆕 Central settings (future)
│
├── schema_registry.py                   ✅ Created
│
├── streamlit_app/                       ✅ KEEP + REORGANIZE
│   ├── main_app.py                     ✅ Keep
│   ├── core/                           🔄 REORGANIZE
│   │   ├── __init__.py                 🆕 Add package marker
│   │   ├── formatters.py               🆕 Use SchemaRegistry
│   │   ├── data_paths.py              ✅ Keep (good!)
│   │   ├── config.py                  🔄 Migrate to SchemaRegistry
│   │   └── models/                     ✅ Keep
│   ├── pages/                          🔄 SPLIT INTO SMALLER FILES
│   │   ├── company/                    🆕 Modular approach
│   │   │   ├── company_dashboard.py   (main, 200 LOC)
│   │   │   ├── metrics_section.py     (extracted, 150 LOC)
│   │   │   ├── charts_section.py      (extracted, 200 LOC)
│   │   │   └── filters.py             (extracted, 100 LOC)
│   │   ├── bank/                       🆕 Similar structure
│   │   ├── securities/                 🆕 Similar structure
│   │   └── ... (other dashboards)
│   ├── components/                     🔄 EXPAND (extract from pages)
│   │   ├── __init__.py                 🆕
│   │   ├── symbol_selector.py         🆕 Extract from pages
│   │   ├── date_range_picker.py       🆕 Extract from pages
│   │   ├── metric_card.py             🆕 Extract from pages
│   │   └── data_table.py              🆕 Extract from pages
│   └── ... (other folders stay same)
│
├── data_processor/                      ✅ KEEP + REORGANIZE
│   ├── __init__.py                     🆕 Add package marker
│   ├── core/                           🔄 REORGANIZE
│   │   ├── __init__.py                 🆕
│   │   ├── base_calculator.py         🆕 Phase 0.2 will create
│   │   ├── unified_mapper.py          ✅ Keep
│   │   ├── ohlcv_formatter.py         ✅ Keep → Use SchemaRegistry
│   │   ├── ohlcv_validator.py         ✅ Keep → Use SchemaRegistry
│   │   └── ... (other core files)
│   ├── fundamental/                    🔄 REORGANIZE
│   │   ├── __init__.py                 🆕
│   │   ├── base/                       🆕 NEW
│   │   │   └── base_financial_calculator.py  (Phase 0.2)
│   │   ├── company/                    ✅ Keep
│   │   ├── bank/                       ✅ Keep
│   │   ├── insurance/                  ✅ Keep
│   │   └── security/                   ✅ Keep
│   ├── technical/                      🔄 FLATTEN + REORGANIZE
│   │   ├── __init__.py                 🆕
│   │   ├── ohlcv/                      🔄 Flatten from technical/technical/ohlcv
│   │   │   ├── __init__.py             🆕
│   │   │   └── ohlcv_daily_updater.py ✅ Move from nested
│   │   ├── indicators/                 🔄 Flatten from technical/technical/technical_indicators
│   │   │   ├── __init__.py             🆕
│   │   │   ├── technical_processor.py
│   │   │   ├── market_breadth_processor.py
│   │   │   └── ... (other indicators)
│   │   ├── commodity/                  🔄 Flatten
│   │   ├── macro/                      🔄 Flatten
│   │   ├── daily_ohlcv_update.py      ✅ Keep
│   │   └── daily_macro_commodity_update.py ✅ Keep
│   ├── valuation/                      ✅ KEEP (structure is good)
│   ├── news/                           ✅ KEEP
│   ├── Bsc_forecast/                   ✅ KEEP
│   └── logs/                           🔄 MOVE → /logs/processors/
│
├── data_warehouse/                      ✅ KEEP (structure is good)
│   ├── raw/                            ✅ Keep
│   ├── metadata/                       ✅ Keep (source of truth)
│   │   ├── metric_registry.json       ✅ Keep
│   │   ├── sector_industry_registry.json ✅ Keep
│   │   └── data_warehouse_schema.json 🔄 Move → /config/schemas/metadata/
│   └── schemas/                        ⚠️ DEPRECATE (move to /config/schemas/data/)
│
├── calculated_results/                  ✅ KEEP
│   ├── schemas/                        ⚠️ DEPRECATE (move to /config/schemas/)
│   └── ... (other folders keep)
│
├── copy/                                ❌ DELETE (technical debt)
│
├── logs/                                🆕 NEW CENTRALIZED
│   ├── processors/                     🔄 Move from data_processor/logs/
│   ├── streamlit/                      🆕 New
│   └── mcp/                            🔄 Move MCP logs here
│
├── mongodb/                             ✅ KEEP
├── mcp_server/                          ✅ KEEP (rename to `mcp/` later)
├── scripts/                             ✅ KEEP
└── docs/                                ✅ KEEP + UPDATE

```

---

## 🗺️ REORGANIZATION ROADMAP

### Phase 1: Schema Consolidation (Week 1) - PRIORITY

#### Week 1.1: Setup Central Schemas (2 days)
- [x] Create `/config/schemas/` directory structure
- [x] Create `master_schema.json` with global settings
- [x] Create `schema_registry.py`
- [ ] Create symlinks for registries
  ```bash
  cd config/schemas/metadata
  ln -s ../../../data_warehouse/metadata/metric_registry.json
  ln -s ../../../data_warehouse/metadata/sector_industry_registry.json
  ```

#### Week 1.2: Consolidate Schemas (3 days)
- [ ] **Consolidate OHLCV** (1 day)
  - Merge `calculated_results/schemas/ohlcv_data_schema.json`
  - Merge `data_warehouse/schemas/ohlcv_schema.json`
  - Create `config/schemas/data/ohlcv.json`
  - Test with `OHLCVFormatter` and `OHLCVValidator`

- [ ] **Consolidate Fundamental** (1 day)
  - Merge `calculated_results/schemas/fundamental_calculated_schema.json`
  - Merge `data_warehouse/schemas/fundamental_schema.json`
  - Create `config/schemas/data/fundamental.json`

- [ ] **Consolidate Technical** (1 day)
  - Merge `calculated_results/schemas/technical_calculated_schema.json`
  - Merge `data_warehouse/schemas/technical_schema.json`
  - Create `config/schemas/data/technical.json`

#### Week 1.3: Update Code (2 days)
- [ ] Update `OHLCVFormatter` to use `SchemaRegistry`
- [ ] Update `OHLCVValidator` to use `SchemaRegistry`
- [ ] Create `streamlit_app/core/formatters.py` wrapper
- [ ] Update 2-3 Streamlit pages as proof of concept

---

### Phase 2: Package Structure (Week 2) - FOUNDATION

#### Week 2.1: Add `__init__.py` Files (1 day)
```bash
# Add package markers to all modules
touch data_processor/__init__.py
touch data_processor/core/__init__.py
touch data_processor/fundamental/__init__.py
touch data_processor/fundamental/base/__init__.py
touch data_processor/fundamental/company/__init__.py
touch data_processor/fundamental/bank/__init__.py
touch data_processor/fundamental/insurance/__init__.py
touch data_processor/fundamental/security/__init__.py
touch data_processor/technical/__init__.py
touch data_processor/technical/ohlcv/__init__.py
touch data_processor/technical/indicators/__init__.py
touch data_processor/valuation/__init__.py
touch data_processor/news/__init__.py

touch streamlit_app/__init__.py
touch streamlit_app/core/__init__.py
touch streamlit_app/components/__init__.py
touch streamlit_app/pages/__init__.py
touch streamlit_app/features/__init__.py
touch streamlit_app/services/__init__.py
```

#### Week 2.2: Remove `sys.path` Hacks (2 days)
- [ ] Identify all 40+ files with `sys.path.insert()`
- [ ] Replace with relative imports
  ```python
  # Before
  import sys
  sys.path.insert(0, str(Path(__file__).parent.parent))
  from data_processor.core import utils

  # After
  from ..core import utils
  ```

#### Week 2.3: Centralize Paths (1 day)
- [ ] Update all hardcoded paths to use `streamlit_app/core/data_paths.py`
- [ ] Add data_paths.py equivalentfor `data_processor`

#### Week 2.4: Flatten Technical (1 day)
```bash
# Move files from nested technical/technical/ to technical/
mv data_processor/technical/technical/ohlcv/* data_processor/technical/ohlcv/
mv data_processor/technical/technical/commodity/* data_processor/technical/commodity/
mv data_processor/technical/technical/macro/* data_processor/technical/macro/
mv data_processor/technical/technical/technical_indicators/* data_processor/technical/indicators/

# Remove empty directories
rmdir data_processor/technical/technical/ohlcv
rmdir data_processor/technical/technical/commodity
rmdir data_processor/technical/technical/macro
rmdir data_processor/technical/technical/technical_indicators
rmdir data_processor/technical/technical
```

---

### Phase 3: Code Cleanup (Week 3) - DEBT REDUCTION

#### Week 3.1: Delete `/copy` Directory (1 hour)
```bash
# Verify no active usage
grep -r "import.*copy\." . | grep -v ".git" | grep -v "__pycache__"

# If safe, delete
rm -rf copy/
```

#### Week 3.2: Centralize Logs (1 day)
```bash
# Create centralized logs structure
mkdir -p logs/processors
mkdir -p logs/streamlit
mkdir -p logs/mcp

# Move existing logs
mv data_processor/logs/* logs/processors/ 2>/dev/null || true

# Move root logs
mv *.log logs/processors/ 2>/dev/null || true
```

#### Week 3.3: Split Large Page Files (2 days)
For each dashboard (company, bank, securities):
```
Before:
pages/company_dashboard.py (1,207 LOC)

After:
pages/company/
├── __init__.py
├── company_dashboard.py        (200 LOC - main orchestration)
├── metrics_section.py          (150 LOC - metrics display)
├── charts_section.py           (200 LOC - chart rendering)
├── filters.py                  (100 LOC - filters/selectors)
└── utils.py                    (50 LOC - page-specific utils)
```

---

### Phase 4: Documentation (Week 3-4) - KNOWLEDGE

#### Week 4.1: Update Documentation (2 days)
- [ ] Update `CLAUDE.md` with new structure
- [ ] Update `README.md` (if exists)
- [ ] Create `docs/NEW_STRUCTURE.md`
- [ ] Update import examples in all docs

#### Week 4.2: Migration Guide (1 day)
- [ ] Document breaking changes
- [ ] Provide migration examples
- [ ] Update MASTER_PLAN.md

---

## 🔧 DETAILED MIGRATION STEPS

### Step 1: Schema Consolidation (DO THIS FIRST)

```bash
# 1. Create structure
mkdir -p config/schemas/{data,display,metadata}

# 2. Consolidate OHLCV
# Manually merge:
# - calculated_results/schemas/ohlcv_data_schema.json (display formats)
# - data_warehouse/schemas/ohlcv_schema.json (data structure)
# Into: config/schemas/data/ohlcv.json

# 3. Test
python3 config/schema_registry.py  # Should work
python3 data_processor/core/test_ohlcv_standardization.py  # Should pass
```

### Step 2: Update Formatters

```python
# OLD: data_processor/core/ohlcv_formatter.py
class OHLCVFormatter:
    def __init__(self, schema_path=None):
        if schema_path is None:
            root = Path(__file__).resolve().parents[2]
            schema_path = root / "calculated_results/schemas/ohlcv_data_schema.json"
        with open(schema_path) as f:
            self.schema = json.load(f)

# NEW: Use SchemaRegistry
from config.schema_registry import SchemaRegistry

class OHLCVFormatter:
    def __init__(self):
        self.registry = SchemaRegistry()

    def format_price(self, value, include_currency=True):
        return self.registry.format_price(value, include_currency)
```

### Step 3: Flatten Technical

```bash
# Before
data_processor/technical/technical/ohlcv/

# After
data_processor/technical/ohlcv/

# Command
mv data_processor/technical/technical/* data_processor/technical/
rmdir data_processor/technical/technical
```

### Step 4: Add Package Markers

```bash
# Create __init__.py in all directories
find data_processor -type d -exec touch {}/__init__.py \;
find streamlit_app -type d -exec touch {}/__init__.py \;
```

---

## 📊 MIGRATION CHECKLIST

### Pre-Flight Checks
- [ ] Full backup created (`git tag v1.0-before-reorganization`)
- [ ] All tests passing
- [ ] Schema consolidation plan reviewed

### Week 1: Schemas
- [x] Create `config/schemas/` structure
- [x] Create `master_schema.json`
- [x] Create `schema_registry.py`
- [x] Test `SchemaRegistry` works
- [ ] Create symlinks for registries
- [ ] Consolidate OHLCV schema
- [ ] Consolidate Fundamental schema
- [ ] Consolidate Technical schema
- [ ] Update `OHLCVFormatter` to use registry
- [ ] Update `OHLCVValidator` to use registry
- [ ] Test with 2-3 Streamlit pages

### Week 2: Package Structure
- [ ] Add all `__init__.py` files
- [ ] Remove `sys.path` hacks (40+ files)
- [ ] Centralize path resolution
- [ ] Flatten `technical/technical/` structure
- [ ] Update all imports
- [ ] Test all processors work

### Week 3: Cleanup
- [ ] Delete `/copy` directory
- [ ] Centralize all logs
- [ ] Split company_dashboard.py
- [ ] Split bank_dashboard.py
- [ ] Split securities_dashboard.py
- [ ] Test all dashboards work

### Week 4: Documentation
- [ ] Update `CLAUDE.md`
- [ ] Update `MASTER_PLAN.md`
- [ ] Create migration guide
- [ ] Update architecture docs

---

## ⚠️ RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking imports | HIGH | Gradual migration, keep old paths temporarily |
| Schema conflicts | MEDIUM | Thorough merging, validation tests |
| Lost functionality | HIGH | Comprehensive testing before/after |
| Team confusion | MEDIUM | Clear documentation, migration guide |

---

## 🎯 SUCCESS CRITERIA

After reorganization, we should have:

✅ **Schema Management**
- Single source of truth: `/config/schemas/master_schema.json`
- All formatters use `SchemaRegistry`
- No scattered schema files

✅ **Package Structure**
- No `sys.path` hacks (0 out of 40+)
- All directories have `__init__.py`
- Clean relative imports

✅ **Code Organization**
- No `/copy` directory
- No `technical/technical/` nesting
- Page files < 500 LOC each
- Centralized logs in `/logs/`

✅ **Testing**
- All existing tests still pass
- New tests for SchemaRegistry
- Visual regression tests for Streamlit

---

## 📞 NEXT STEPS

### Immediate (Today)
1. Review this plan
2. Create backup: `git tag v1.0-before-reorganization`
3. Start Week 1.2: Consolidate OHLCV schema

### This Week
1. Complete schema consolidation
2. Update formatters/validators
3. Test with Streamlit pages

### Next Week
1. Add package structure
2. Remove sys.path hacks
3. Flatten technical directory

---

**Last Updated:** 2025-12-07
**Status:** Ready to Execute
**Priority:** 🔴 CRITICAL - Start Immediately

