# 🗂️ Schema Consolidation Plan

**Goal:** Migrate from scattered schemas to centralized Schema Registry
**Status:** Design Complete ✅ | Migration In Progress
**Date:** 2025-12-07

---

## 📊 Current State Analysis

### Schema Files Found (10 files in 3 locations)

```
/calculated_results/schemas/ (4 files)
├── fundamental_calculated_schema.json
├── ohlcv_data_schema.json
├── technical_calculated_schema.json
└── valuation_calculated_schema.json

/data_warehouse/schemas/ (3 files)
├── fundamental_schema.json
├── ohlcv_schema.json
└── technical_schema.json

/data_warehouse/metadata/ (3 files)
├── metric_registry.json         ← KEEP (source of truth)
├── sector_industry_registry.json ← KEEP (source of truth)
└── data_warehouse_schema.json
```

**Problems:**
- ❌ Duplication: `ohlcv_schema.json` exists in 2 places
- ❌ Inconsistency: Different formatting rules across schemas
- ❌ Hard to update: Need to update 3+ files to change global settings
- ❌ No central theme: Colors scattered across code

---

## 🎯 Target State

### New Structure

```
/config/schemas/ (Centralized)
├── master_schema.json                  ✅ CREATED - Global settings
├── README.md                           ✅ CREATED
│
├── data/ (Data schemas)
│   ├── fundamental.json               ⏳ TODO - Consolidate
│   ├── technical.json                 ⏳ TODO - Consolidate
│   ├── ohlcv.json                     ⏳ TODO - Consolidate
│   └── valuation.json                 ⏳ TODO - Consolidate
│
├── display/ (UI schemas)
│   ├── formatting_rules.json          ⏳ TODO - Extract from master
│   ├── color_theme.json               ⏳ TODO - Extract from master
│   └── chart_defaults.json            ⏳ TODO - Extract from master
│
└── metadata/ (Symlinks to data_warehouse)
    ├── metric_registry.json → /data_warehouse/metadata/metric_registry.json
    └── sector_registry.json → /data_warehouse/metadata/sector_industry_registry.json

/config/
└── schema_registry.py                  ✅ CREATED - Central manager
```

---

## 🔧 Migration Strategy

### Phase 1: Setup (DONE ✅)

- [x] Create `/config/schemas/` directory
- [x] Create `master_schema.json` with global settings
- [x] Create `schema_registry.py` central manager
- [x] Test SchemaRegistry works

### Phase 2: Consolidate Schemas (TODO)

#### Step 1: Create Symlinks for Registries
```bash
cd /Users/buuphan/Dev/stock_dashboard/config/schemas/metadata
ln -s ../../../data_warehouse/metadata/metric_registry.json metric_registry.json
ln -s ../../../data_warehouse/metadata/sector_industry_registry.json sector_registry.json
```

**Why symlinks?**
- Keep source of truth in `/data_warehouse/metadata/`
- Single location to update
- Backward compatibility

#### Step 2: Consolidate OHLCV Schema
```bash
# Merge ohlcv_data_schema.json + ohlcv_schema.json → config/schemas/data/ohlcv.json
# Keep best parts from both
```

**Action:**
```python
# File: config/schemas/data/ohlcv.json
# Merge:
# - Display formats from ohlcv_data_schema.json
# - Validation rules from ohlcv_data_schema.json
# - Data structure from ohlcv_schema.json
# - Inherit global settings from master_schema.json
```

#### Step 3: Consolidate Fundamental Schema
```bash
# Merge fundamental_calculated_schema.json + fundamental_schema.json
# → config/schemas/data/fundamental.json
```

#### Step 4: Consolidate Technical Schema
```bash
# Similar merge for technical schemas
```

#### Step 5: Consolidate Valuation Schema
```bash
# Move valuation_calculated_schema.json
```

### Phase 3: Update Code to Use SchemaRegistry (TODO)

#### Priority 1: Update Formatters (HIGH)

**Before:**
```python
# OLD: data_processor/core/ohlcv_formatter.py
from pathlib import Path
import json

class OHLCVFormatter:
    def __init__(self, schema_path=None):
        if schema_path is None:
            root = Path(__file__).resolve().parents[2]
            schema_path = root / "calculated_results/schemas/ohlcv_data_schema.json"

        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
```

**After:**
```python
# NEW: Use SchemaRegistry
from config.schema_registry import SchemaRegistry

class OHLCVFormatter:
    def __init__(self):
        self.registry = SchemaRegistry()
        # All formatting now uses registry methods

    def format_price(self, value):
        # Delegate to registry
        return self.registry.format_price(value)
```

#### Priority 2: Update Streamlit Pages (HIGH)

**Before:**
```python
# OLD: Scattered formatting
price_str = f"{price:,.2f}đ"
volume_str = f"{volume:,}"
pct_str = f"{pct:.2f}%"

# Hardcoded colors
st.markdown(f'<span style="color: #00C853">{pct_str}</span>', unsafe_allow_html=True)
```

**After:**
```python
# NEW: Use SchemaRegistry
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()
price_str = registry.format_price(price)
volume_str = registry.format_volume(volume)
pct_str = registry.format_percentage(pct, show_sign=True)

# Use theme colors
color = registry.get_color('positive_change')
st.markdown(f'<span style="color: {color}">{pct_str}</span>', unsafe_allow_html=True)
```

#### Priority 3: Update Validators (MEDIUM)

```python
# OLD: Load schema in validator
class OHLCVValidator:
    def __init__(self, schema_path=None):
        with open(schema_path) as f:
            self.schema = json.load(f)

# NEW: Use SchemaRegistry
class OHLCVValidator:
    def __init__(self):
        self.registry = SchemaRegistry()
        self.schema = self.registry.get_schema('ohlcv')
```

### Phase 4: Deprecate Old Schemas (TODO)

```bash
# Move old schemas to archive
mkdir -p archive/schemas_v1
mv calculated_results/schemas/* archive/schemas_v1/
mv data_warehouse/schemas/* archive/schemas_v1/
mv data_warehouse/metadata/data_warehouse_schema.json archive/schemas_v1/

# Update .gitignore
echo "archive/schemas_v1/" >> .gitignore
```

---

## 📋 Migration Checklist

### Setup (Week 1)
- [x] Create central schema structure
- [x] Create master_schema.json
- [x] Create SchemaRegistry class
- [x] Test SchemaRegistry works
- [ ] Create symlinks for registries
- [ ] Consolidate OHLCV schemas
- [ ] Consolidate Fundamental schemas
- [ ] Consolidate Technical schemas
- [ ] Consolidate Valuation schemas

### Code Migration (Week 2)
- [ ] Update OHLCVFormatter to use SchemaRegistry
- [ ] Update OHLCVValidator to use SchemaRegistry
- [ ] Create Streamlit helper: `streamlit_app/core/formatters.py`
- [ ] Update 5 most-used Streamlit pages
- [ ] Update data processors
- [ ] Update validators

### Testing (Week 2)
- [ ] Test all formatters work
- [ ] Test all validators work
- [ ] Test Streamlit app works
- [ ] Visual regression testing (screenshots before/after)
- [ ] Performance testing

### Cleanup (Week 3)
- [ ] Archive old schemas
- [ ] Update all documentation
- [ ] Update CLAUDE.md
- [ ] Create migration guide for team

---

## 🎯 Benefits After Migration

### Before (Current)
```python
# Different formatting in different files
# File 1:
price_str = f"{price:,.2f}đ"

# File 2:
price_str = f"{price:.2f} VND"

# File 3:
from data_processor.core.ohlcv_formatter import OHLCVFormatter
formatter = OHLCVFormatter()
price_str = formatter.format_price(price)
```

### After (Target)
```python
# EVERYWHERE uses same SchemaRegistry
from config.schema_registry import format_price

price_str = format_price(price)  # "25,750.50đ"
```

**Benefits:**
1. ✅ **Consistency:** All prices formatted the same way
2. ✅ **Maintainability:** Change format in 1 place → affects entire app
3. ✅ **Theme support:** Easy to switch themes (light/dark)
4. ✅ **Performance:** Schema loaded once (singleton)
5. ✅ **Type safety:** Clear API, less errors

---

## 🚀 Quick Start Guide

### For New Code (Use Immediately)

```python
# 1. Import SchemaRegistry
from config.schema_registry import SchemaRegistry

# 2. Get instance (singleton)
registry = SchemaRegistry()

# 3. Use formatting
price = registry.format_price(25750.5)
volume = registry.format_volume(1250000)
pct = registry.format_percentage(2.35, show_sign=True)

# 4. Use colors
positive_color = registry.get_color('positive_change')
entity_color = registry.get_entity_color('BANK')

# 5. Use validation
pe_range = registry.get_validation_threshold('pe_ratio', 'typical_range')
```

### For Streamlit Pages

```python
# streamlit_app/pages/your_page.py
import streamlit as st
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()

# Page config with theme
st.set_page_config(
    page_title=registry.app_name,
    page_icon="📊"
)

# Inject CSS theme
st.markdown(registry.get_streamlit_theme_css(), unsafe_allow_html=True)

# Use formatting
st.metric(
    label="Stock Price",
    value=registry.format_price(price),
    delta=registry.format_percentage(change_pct)
)
```

---

## ⚠️ Breaking Changes

### None (Backward Compatible)

- Old formatters still work (for now)
- Old schema paths still exist (for now)
- Gradual migration recommended

### Deprecation Timeline

- **Week 1-2:** New code uses SchemaRegistry, old code unchanged
- **Week 3-4:** Migrate existing code gradually
- **Week 5:** Archive old schemas (after verification)
- **Week 6+:** Remove old formatters (breaking change)

---

## 📊 Progress Tracking

| Task | Status | Owner | Due Date |
|------|--------|-------|----------|
| Create master_schema.json | ✅ Done | Claude | 2025-12-07 |
| Create SchemaRegistry | ✅ Done | Claude | 2025-12-07 |
| Test SchemaRegistry | ✅ Done | Claude | 2025-12-07 |
| Consolidate OHLCV schemas | ⏳ Todo | - | - |
| Update OHLCVFormatter | ⏳ Todo | - | - |
| Update Streamlit pages | ⏳ Todo | - | - |
| Archive old schemas | ⏳ Todo | - | - |

---

## 📞 Questions?

**Q: Do I need to update all code at once?**
A: No! Gradual migration is fine. New code uses SchemaRegistry, old code continues working.

**Q: Will old formatters break?**
A: No, they'll continue working until we explicitly remove them (Week 6+).

**Q: How do I test my migration?**
A: Visual comparison - screenshot before/after, verify numbers are identical.

**Q: What if I need custom formatting?**
A: Override in your code, but prefer updating master_schema.json for global changes.

---

**Last Updated:** 2025-12-07
**Next Review:** After Week 1 consolidation
