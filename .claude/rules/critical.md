# Critical Rules (Non-Negotiable)

**READ THIS FIRST before making any code changes.**

These are non-negotiable constraints that MUST be followed in ALL situations.

---

## Rule 1: Update Existing Documentation, Don't Create New Files

**ALWAYS update existing markdown files instead of creating new ones.**

When documenting:
- ✅ **DO**: Update existing `.md` files in `plans/` or root directory
- ✅ **DO**: Append new sections to existing documentation
- ✅ **DO**: Use clear section headers (##, ###) for organization
- ❌ **DON'T**: Create new `.md` files unless explicitly requested
- ❌ **DON'T**: Duplicate information across multiple files
- ❌ **DON'T**: Create "part 1", "part 2" files - use sections instead

**Primary Documentation Locations:**
- `plans/*.md` - Active development plans (update these!)
- `CLAUDE.md` - This file (project instructions)
- `README.md` - User-facing documentation
- `docs/archive/` - Historical documentation (read-only)

**Example:**
```python
# ❌ WRONG: Creating new file
write_file("NEW_FEATURE_PLAN_PART2.md", content)

# ✅ CORRECT: Update existing plan
append_to_file("plans/main_plan.md", "## New Feature\n\n" + content)
```

---

## Rule 2: Check for Existing Plans Before Creating

Before creating any documentation:
1. Search for existing plan files: `find plans -name "*.md"`
2. If similar plan exists, update it
3. If creating new plan is necessary, consolidate related content first

---

## Rule 3: ALWAYS Use Registries (CRITICAL)

**When building new features, ALWAYS use the registry system:**

```python
# Import from canonical locations
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# Metric lookup
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")
roe_formula = metric_reg.get_calculated_metric_formula("roe")

# Sector/ticker lookup
sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker("ACB")
peers = sector_reg.get_peers("ACB")  # Returns other banking tickers

# Schema access
schema_reg = SchemaRegistry()
ohlcv_schema = schema_reg.get_schema('ohlcv')
formatted_price = schema_reg.format_price(25750.5)  # "25,750.50đ"
```

**Why this is CRITICAL:**
- Single source of truth for all metrics, sectors, tickers
- Prevents hardcoding Vietnamese metric names
- Ensures consistency across codebase
- Enables rapid development

---

## Rule 4: Path Resolution (✅ COMPLETED - Now Standard)

**STATUS: ✅ EXCELLENT (100% compliance)**

### Audit Results (2025-12-28):
- ✅ ZERO files using deprecated paths
- ✅ ALL files use `DATA/processed/`, `DATA/raw/`
- ✅ Path migration COMPLETED

### Current Standard (v4.0.0):

```python
# ✅ CORRECT - Manual construction
from pathlib import Path
data_path = Path("DATA/processed/fundamental/company")

# ✅ BETTER - Centralized helper (recommended)
from PROCESSORS.core.config.paths import get_data_path
data_path = get_data_path("processed", "fundamental", "company")
```

### Deprecated Paths (NO LONGER USED):
- ❌ `calculated_results/` - REMOVED
- ❌ `data_warehouse/raw/` - REMOVED
- ❌ `DATA/refined/` - REMOVED

**Canonical v4.0.0 Structure:**
```
DATA/
├── raw/                    # Input data (READ from here)
│   ├── ohlcv/
│   ├── fundamental/csv/
│   ├── commodity/
│   └── macro/
│
└── processed/              # Output data (WRITE to here)
    ├── fundamental/
    │   ├── company/
    │   ├── bank/
    │   ├── insurance/
    │   └── security/
    ├── technical/
    ├── valuation/
    ├── commodity/
    ├── macro/
    └── forecast/bsc/
```

---

## Rule 5: Use Existing Calculators (Don't Duplicate)

**NEVER reimplement financial calculations. Use existing calculators.**

```python
# ✅ CORRECT: Load existing calculated results
import pandas as pd

company_metrics = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_metrics = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
technical_data = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
```

**If you need NEW calculations:**
```python
# ✅ Use transformer functions (pure functions)
from PROCESSORS.transformers.financial import roe, gross_margin, yoy_growth

sector_avg_roe = roe(total_net_income, total_equity)
sector_growth = yoy_growth(current_revenue, previous_revenue)
```

**Available Calculators:**
- `PROCESSORS/fundamental/calculators/company_calculator.py`
- `PROCESSORS/fundamental/calculators/bank_calculator.py`
- `PROCESSORS/fundamental/calculators/insurance_calculator.py`
- `PROCESSORS/fundamental/calculators/security_calculator.py`
- `PROCESSORS/valuation/calculators/*` (PE, PB, EV/EBITDA)
- `PROCESSORS/technical/indicators/*` (MA, RSI, MACD, etc.)

---

## 🛡️ Anti-Hallucination Safeguards

**These rules prevent AI from generating broken/hallucinated code.**

### Rule 6: Verify File Existence

**BEFORE referencing any file path:**

```python
# ❌ WRONG (hallucination risk)
from PROCESSORS.fancy_new_module import cool_function  # Does this file exist?

# ✅ CORRECT (verified)
# 1. First: Use Glob tool to find file
# 2. Then: Read file to confirm function exists
# 3. Then import
```

**Enforcement:**
- If file location uncertain → Use `Glob` pattern search
- If file found → `Read` before import
- If not found → Ask user for correct path
- NEVER assume file location based on "typical project structure"

---

### Rule 7: Schema Validation (Data Structure)

**BEFORE accessing DataFrame columns:**

```python
# ❌ WRONG (column name assumption)
df['roe_ratio']  # Does this column exist? Unknown!

# ✅ CORRECT (verified)
# 1. Read file: df = pd.read_parquet(path)
# 2. Check columns: print(df.columns.tolist())
# 3. Confirm 'roe' exists (not 'roe_ratio')
# 4. Then: df['roe']
```

**Why Critical:**
- Column names vary across entity types (company, bank, insurance)
- Vietnamese → English mapping can differ
- Parquet schemas must be validated before access

---

### Rule 8: Don't Reinvent the Wheel

**BEFORE implementing any calculation:**

```python
# ❌ WRONG (duplicating existing code)
def calculate_roe(net_income, equity):
    return net_income / equity

# ✅ CORRECT (using existing)
from PROCESSORS.transformers.financial import roe
sector_roe = roe(total_net_income, total_equity)
```

**Verification Steps:**
1. Check `.claude/reference/formulas.md` for existing formulas
2. Search: `Grep("def calculate_", path="PROCESSORS/transformers")`
3. If found → Import and reuse
4. If not found → Implement with tests

---

### Rule 9: Test Before Claim

**BEFORE claiming "implementation complete":**

```bash
# ❌ WRONG
"I've implemented the calculator. It should work."

# ✅ CORRECT (with evidence)
1. python3 PROCESSORS/fundamental/calculators/company_calculator.py
2. ls -lh DATA/processed/fundamental/company/
3. python3 -c "import pandas as pd; print(pd.read_parquet('output.parquet').head())"
4. "✅ Confirmed: File exists, 1,234 rows, expected columns present"
```

**Enforcement:**
- No "done" without execution proof
- Verify output files exist
- Inspect first 5 rows of output data
- Check for errors in logs

---

### Rule 10: Docs-Code Sync

**BEFORE updating code that's documented:**

```python
# Changing this function signature:
def calculate_pe(market_cap: float, earnings: float) -> float:
    ...

# Must also update:
# - .claude/reference/formulas.md (PE formula section)
# - .claude/guides/architecture.md (if location changed)
```

**Check Before Change:**
```bash
# Search documentation for references
grep -r "calculate_pe" .claude/
# Update any matching documentation
```

---

### Rule 11: Library Version Check

**BEFORE using external library methods:**

```python
# ❌ WRONG (API assumption from training data)
df['rsi'] = ta.momentum.rsi_indicator(df['close'])  # Does this exist?

# ✅ CORRECT (verified API)
# 1. python3 -c "import ta; print(dir(ta.momentum))"
# 2. Confirm rsi_indicator exists
# 3. Check signature: help(ta.momentum.rsi_indicator)
# 4. Then use
```

**Project-Specific:**
- **Python 3.13:** `dict | list` syntax OK
- **Pandas 2.x:** NO `df.append()`, YES `pd.concat()`
- **ta-lib:** Verify method availability first

---

### Rule 12: No Placeholder Code

**WHEN implementing code:**

```python
# ❌ WRONG (placeholder hell)
def process_data(df):
    # Validate data
    # TODO: implement validation

    # Calculate metrics
    # ... calculation code here ...

    return result

# ✅ CORRECT (complete implementation)
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    # Validate data
    if df.empty:
        raise ValueError("Empty DataFrame")
    if 'ticker' not in df.columns:
        raise ValueError("Missing 'ticker' column")

    # Calculate metrics
    df['roe'] = df['net_income'] / df['equity']
    df['roa'] = df['net_income'] / df['assets']

    return df
```

**Forbidden Patterns:**
- ❌ `# TODO: implement later`
- ❌ `# ... rest of code ...`
- ❌ `pass  # placeholder`
- ❌ `# code continues here`

---

### Rule 13: Environment Awareness

**BEFORE running commands:**

```bash
# ❌ WRONG (CWD assumption)
python3 scripts/process.py  # Where are we running this?

# ✅ CORRECT (verified context)
# 1. pwd  # Confirm: /Users/buuphan/Dev/Vietnam_dashboard
# 2. python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Project Environment:**
- **Expected CWD:** `/Users/buuphan/Dev/Vietnam_dashboard`
- **Python Binary:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`
- **No virtual environment** - Uses global Python 3.13

---

## Summary: 13 Critical Rules

### Documentation Rules (1-2)
1. **Update existing docs** (don't create new .md files)
2. **Check existing plans** before creating new ones

### Architecture Rules (3-5)
3. **ALWAYS use registries** (MetricRegistry, SectorRegistry, SchemaRegistry)
4. **ALWAYS use canonical paths** (`DATA/processed/`, `DATA/raw/`)
5. **NEVER duplicate calculators** (use existing from `PROCESSORS/`)

### Anti-Hallucination Rules (6-13)
6. **Verify file existence** (Glob → Read → Import)
7. **Validate schemas** (check columns before access)
8. **Don't reinvent wheel** (search existing implementations)
9. **Test before claim** (run code, verify output)
10. **Sync docs with code** (update docs when changing code)
11. **Check library versions** (verify API methods exist)
12. **No placeholder code** (complete implementations only)
13. **Environment awareness** (verify CWD, Python binary)

---

## Violation Consequences

Breaking these rules will cause:
- **Import errors** (phantom modules, wrong paths)
- **Runtime errors** (missing columns, wrong methods)
- **Data inconsistency** (hardcoded values, duplicate logic)
- **Maintenance nightmares** (outdated docs, incomplete code)
- **Technical debt** (duplicated calculators, placeholder hell)

**When in doubt, read this file first.**
