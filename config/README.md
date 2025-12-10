# Configuration & Registry System Documentation

**Last Updated:** 2025-12-10
**Status:** Canonical structure established, duplicates removed

---

## 📁 Directory Structure

```
config/
├── registries/                    # Registry lookup classes (Python)
│   ├── metric_lookup.py          # MetricRegistry - Financial metrics lookup
│   ├── sector_lookup.py          # SectorRegistry - Ticker/sector mapping
│   └── builders/                 # Registry builder scripts
│       ├── build_metric_registry.py
│       └── build_sector_registry.py
│
├── schema_registry.py            # SchemaRegistry singleton (master)
├── schema_registry/              # Organized schema definitions
│   ├── core/                     # Core type/entity schemas
│   ├── domain/                   # Domain-specific schemas
│   │   ├── fundamental/
│   │   ├── technical/
│   │   ├── valuation/
│   │   └── unified/
│   └── display/                  # UI/visualization schemas
│
├── metadata_registry/            # Metadata & lookup data (JSON)
│   ├── metrics/
│   ├── sectors/
│   ├── tickers/
│   └── config/
│
├── business_logic/               # Business rules & configurations
│   ├── analysis/                 # Analysis settings
│   ├── decisions/                # Decision rules
│   └── alerts/                   # Alert configurations
│
└── schemas/                      # LEGACY (backward compatibility)
    ├── master_schema.json
    └── data/
```

---

## 🔧 Registry System

### 1. MetricRegistry (`registries/metric_lookup.py`)

**Purpose:** Fast lookup for financial metrics from BSC database

**Data Source:** \`DATA/metadata/metric_registry.json\` (770 KB, 2,099 metrics)

**Usage:**
```python
from config.registries import MetricRegistry

registry = MetricRegistry()

# Get metric by code
metric = registry.get_metric("CIS_62", "COMPANY")

# Search by Vietnamese name
results = registry.search_by_name("lợi nhuận")

# Get calculated metric formula
roe_formula = registry.get_calculated_metric_formula("roe")
```

**Content:** 4 entity types × 3 categories × 2,099 total metrics + 30+ calculated metrics

---

### 2. SectorRegistry (`registries/sector_lookup.py`)

**Purpose:** Ticker → Entity Type → Sector mapping

**Data Source:** \`DATA/metadata/sector_industry_registry.json\`

**Usage:**
```python
from config.registries import SectorRegistry

registry = SectorRegistry()

# Get ticker information
info = registry.get_ticker("ACB")

# Get peer companies
peers = registry.get_peers("ACB")
```

**Content:** 457 tickers × 19 sectors × 4 entity types

---

### 3. SchemaRegistry (`schema_registry.py`)

**Purpose:** Central schema management + formatting utilities

**Usage:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()  # Singleton

# Formatting
price = registry.format_price(25750.5)           # "25,750.50đ"
volume = registry.format_volume(1_500_000)       # "1.5M"

# Get colors
color = registry.get_color('positive_change')
```

---

## 📝 Migration History

### 2025-12-10: Registry & Schema Cleanup

**Changes:**
1. ✅ Moved: \`PROCESSORS/core/registries/\` → \`config/registries/\`
2. ✅ Removed duplicates:
   - 3 schema files (ohlcv.json, fundamental.json, technical.json)
   - 2 metric_registry.json copies
3. ✅ Deleted legacy \`SchemaRegistry\` in PROCESSORS/core/registries/
4. ✅ Storage saved: ~2.4 MB

**Import Pattern:**
```python
# ✅ CORRECT (canonical)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# ❌ DEPRECATED (will fail)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
```

---

## 🔨 Builder Scripts

### Build Metric Registry
```bash
python3 config/registries/builders/build_metric_registry.py
```
Converts BSC Excel templates → \`DATA/metadata/metric_registry.json\`

### Build Sector Registry
```bash
python3 config/registries/builders/build_sector_registry.py
```
Builds sector/industry registry from ticker metadata

---

## 📞 See Also

- **Project Overview:** \`CLAUDE.md\`
- **Data Management Plan:** \`DATA/metadata/data_management_plan.md\`
- **Active Development Plan:** \`.cursor/plans/\`
