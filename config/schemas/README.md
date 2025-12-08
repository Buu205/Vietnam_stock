# Central Schema Registry

**Purpose:** Single source of truth for ALL schemas in the stock dashboard system

## Why Centralized Schemas?

**Before (Problems):**
- ❌ Schemas scattered across 3 locations
- ❌ Hard to find which schema to use
- ❌ Duplication and inconsistency
- ❌ Difficult to update global settings

**After (Benefits):**
- ✅ All schemas in one location: `/config/schemas/`
- ✅ Single import: `from config.schema_registry import SchemaRegistry`
- ✅ Version controlled
- ✅ Easy to update themes, formats, colors globally

## Directory Structure

```
config/schemas/
├── README.md                          # This file
├── master_schema.json                 # Master schema with global settings
├── data/                              # Data schemas
│   ├── fundamental.json              # Fundamental data schema
│   ├── technical.json                # Technical indicators schema
│   ├── ohlcv.json                    # OHLCV trading data schema
│   └── valuation.json                # Valuation metrics schema
├── display/                           # Display & UI schemas
│   ├── formatting_rules.json         # Global formatting rules
│   ├── color_theme.json              # Color scheme for entire app
│   └── chart_defaults.json           # Default chart configurations
├── metadata/                          # Metadata & registries
│   ├── metric_registry.json          # Metric definitions (link to data_warehouse)
│   ├── sector_registry.json          # Sector classifications (link to data_warehouse)
│   └── data_warehouse_structure.json # Data warehouse organization
└── validation/                        # Validation rules
    ├── data_quality_rules.json       # Quality checks
    └── business_rules.json            # Business logic validation
```

## Schema Hierarchy

```
master_schema.json (Global Settings)
    ├── Inherits → data/fundamental.json
    ├── Inherits → data/technical.json
    ├── Inherits → data/ohlcv.json
    ├── Inherits → display/formatting_rules.json
    └── Inherits → display/color_theme.json
```

## Usage

### For Python Code:
```python
from config.schema_registry import SchemaRegistry

# Load all schemas
registry = SchemaRegistry()

# Get specific schema
ohlcv_schema = registry.get_schema('ohlcv')

# Get formatter
formatter = registry.get_formatter('price')

# Get color
positive_color = registry.get_color('positive_change')
```

### For Streamlit:
```python
from config.schema_registry import SchemaRegistry

st.set_page_config(
    page_title=SchemaRegistry.get_app_name(),
    layout=SchemaRegistry.get_layout(),
)

# Use theme colors
st.markdown(f"<style>{SchemaRegistry.get_css()}</style>")
```

## Migration from Old Structure

Old Location → New Location:
- `calculated_results/schemas/*` → `config/schemas/data/`
- `data_warehouse/schemas/*` → Archive (deprecated)
- `data_warehouse/metadata/*` → Keep (symlink to config/schemas/metadata/)

## Version Control

- Schema version: 2.0.0
- Breaking changes require major version bump
- Backward compatibility maintained for 1 version

Last Updated: 2025-12-07
