# 🏗️ ĐÁNH GIÁ KIẾN TRÚC & ĐỀ XUẤT CẢI TIẾN

**Ngày:** 2025-12-08
**Dự án:** Vietnam Dashboard
**So sánh:** Cấu trúc hiện tại vs Canonical Structure

---

## 📊 TÓM TẮT EXECUTIVE

### Trạng thái hiện tại: ✅ 70% Canonical Compliance

| Khía cạnh | Trạng thái | Đánh giá |
|-----------|------------|----------|
| **Data-Logic Separation** | ✅ | DATA/ và PROCESSORS/ tách biệt rõ ràng |
| **Package Structure** | ✅ | Đầy đủ `__init__.py`, import paths sạch |
| **Path Management** | ✅ | Centralized paths trong `PROCESSORS/core/config/paths.py` |
| **No Duplication** | ✅ | Đã xóa toàn bộ duplicate code |
| **Raw vs Processed** | 🟡 | Cần cải thiện cấu trúc thư mục |
| **Naming Clarity** | 🟡 | Một số tên thư mục chưa tối ưu |
| **Schema Location** | 🔴 | Schema nằm rải rác 3 nơi |
| **Pipeline Structure** | 🟡 | Thiếu orchestrator tập trung |

**Kết luận:** Dự án có nền tảng tốt nhưng cần **5 cải tiến chiến thuật** để đạt 100% canonical compliance.

---

## 🔍 PHÂN TÍCH CHI TIẾT

### 1. ✅ ĐIỂM MẠNH HIỆN CÓ

#### 1.1. Data-Processing Separation
```
Vietnam_dashboard/
├── DATA/          # ✅ Read-only data storage
└── PROCESSORS/    # ✅ Processing logic
```
**Đánh giá:** ✅ Tuyệt vời! Separation of concerns rõ ràng.

#### 1.2. Package Structure
```bash
# ✅ Proper Python packages
PROCESSORS/
├── __init__.py
├── core/__init__.py
├── fundamental/__init__.py
├── technical/__init__.py
└── valuation/__init__.py
```
**Đánh giá:** ✅ Professional, no `sys.path.insert()` hacks.

#### 1.3. Centralized Path Management
```python
# PROCESSORS/core/config/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "DATA"
PROCESSED_DIR = DATA_DIR / "processed"
```
**Đánh giá:** ✅ No hardcoded paths, portable across environments.

#### 1.4. No Technical Debt
- ✅ Deleted old `data_warehouse/`, `calculated_results/`, `data_processor/`
- ✅ All imports fixed and working
- ✅ Reclaimed 1.1GB disk space

---

### 2. 🟡 CẦN CẢI THIỆN

#### 2.1. Raw vs Processed Data Structure

**Vấn đề hiện tại:**
```
DATA/
├── raw/
│   ├── fundamental/
│   │   └── processed/          # ❌ "processed" inside "raw"
│   │       ├── *.csv           # Raw input
│   │       └── *.parquet       # Processed output - WRONG LOCATION
│   ├── market/
│   │   └── ohlcv/
│   │       └── OHLCV_mktcap.parquet  # ❌ Processed data in raw/
│   └── macro/
│       ├── interest_rates.parquet    # ❌ Processed data in raw/
│       └── exchange_rates.parquet
│
└── processed/                   # Actual processed outputs
    ├── fundamental/
    ├── technical/
    └── valuation/
```

**Canonical structure đúng:**
```
DATA/
├── raw/                         # ONLY raw inputs
│   ├── fundamental/
│   │   └── csv/                 # ✅ Clear naming
│   │       ├── Q3_2025/
│   │       │   ├── BANK_BALANCE_SHEET.csv
│   │       │   └── COMPANY_BALANCE_SHEET.csv
│   │       └── Q4_2025/
│   ├── market/
│   │   └── ohlcv/               # ✅ Raw OHLCV only
│   └── macro/
│       ├── csv/                 # ✅ Raw macro data
│       └── api/
│
└── refined/                     # ✅ Renamed from "processed"
    ├── fundamental/
    │   ├── current/             # Latest quarter
    │   │   ├── bank_metrics.parquet
    │   │   ├── company_metrics.parquet
    │   │   ├── insurance_metrics.parquet
    │   │   └── security_metrics.parquet
    │   └── archive/             # Historical quarters
    │       ├── Q3_2025/
    │       └── Q2_2025/
    ├── technical/
    │   ├── indicators/          # Technical indicators
    │   ├── market_breadth/
    │   └── moving_averages/
    ├── valuation/
    │   ├── pe_ratios/
    │   └── sector_pe/
    └── market/
        └── ohlcv_standardized/  # Processed OHLCV
```

**Lợi ích:**
- ✅ Rõ ràng đâu là input, đâu là output
- ✅ Không lẫn lộn raw và processed
- ✅ Dễ backup (chỉ backup refined/)
- ✅ Dễ rollback (xóa refined/ và chạy lại pipeline)

---

#### 2.2. Schema Management

**Vấn đề hiện tại:** Schema rải rác 3 nơi
```
DATA/schemas/                    # ❌ Location 1
config/schemas/                  # ❌ Location 2
PROCESSORS/core/schemas/         # ❌ Location 3 (nếu có)
```

**Canonical structure:**
```
config/
└── schemas/                     # ✅ SINGLE source of truth
    ├── data/                    # Data schemas
    │   ├── ohlcv.json
    │   ├── fundamental.json
    │   └── macro.json
    ├── validation/              # Validation rules
    │   ├── input_validation.json
    │   └── output_validation.json
    └── display/                 # Display formatting
        └── formatters.json
```

**Migration plan:**
```bash
# Consolidate all schemas
mkdir -p config/schemas/{data,validation,display}

# Move from DATA/schemas/
mv DATA/schemas/ohlcv*.json config/schemas/data/

# Create SchemaRegistry
cat > PROCESSORS/core/registries/schema_registry.py << 'EOF'
from pathlib import Path
import json

class SchemaRegistry:
    def __init__(self):
        self.schema_dir = Path(__file__).parents[3] / "config" / "schemas"

    def get_schema(self, category: str, name: str):
        schema_path = self.schema_dir / category / f"{name}.json"
        with open(schema_path) as f:
            return json.load(f)
EOF

# Symlink from DATA/schemas to config/schemas (for compatibility)
ln -s ../../config/schemas DATA/schemas
```

---

#### 2.3. Pipeline Structure

**Vấn đề hiện tại:**
```
PROCESSORS/
├── fundamental/
│   └── calculators/             # Individual calculators
│       ├── company_calculator.py
│       ├── bank_calculator.py
│       └── ...
├── technical/
│   └── pipelines/               # ✅ Có pipeline
│       └── daily_full_technical_pipeline.py
└── valuation/
    └── core/                    # Individual calculators
```

**Canonical structure:**
```
PROCESSORS/
├── extractors/                  # ✅ Load raw data
│   ├── csv_loader.py
│   ├── api_loader.py
│   └── parquet_loader.py
│
├── transformers/                # ✅ Pure calculation logic
│   ├── financial/
│   │   ├── bank_ratios.py       # Pure functions
│   │   ├── company_ratios.py
│   │   └── formulas/
│   │       └── base_formulas.py
│   ├── technical/
│   │   ├── indicators.py
│   │   └── market_breadth.py
│   └── valuation/
│       └── pe_calculators.py
│
└── pipelines/                   # ✅ Orchestrators
    ├── daily_update.py          # Run all daily updates
    ├── quarterly_report.py      # Run quarterly processing
    └── backfill.py              # Historical data processing
```

**Lợi ích:**
- ✅ Clear separation: data loading vs calculation vs orchestration
- ✅ Reusable components: extractors can be used across calculators
- ✅ Easy testing: test transformers independently
- ✅ One-command execution: `python pipelines/daily_update.py`

---

#### 2.4. Naming Conventions

**Vấn đề nhỏ hiện tại:**
- `DATA/processed/` → Nên đổi thành `DATA/refined/` (rõ ràng hơn)
- `PROCESSORS/fundamental/calculators/` → Nên là `PROCESSORS/transformers/financial/`

**Canonical naming:**
```
DATA/
├── raw/          # ✅ Input data (READ ONLY)
└── refined/      # ✅ Output data (rõ hơn "processed")

PROCESSORS/
├── extractors/   # ✅ Load data
├── transformers/ # ✅ Calculate metrics
└── pipelines/    # ✅ Orchestrate
```

---

#### 2.5. Validation System

**Thiếu hiện tại:** Input/output validation

**Canonical validation:**
```python
# PROCESSORS/core/validators/input_validator.py
class InputValidator:
    def validate_csv(self, csv_path: Path, entity_type: str):
        """Validate raw CSV before processing"""
        # 1. File exists
        # 2. Schema matches expected columns
        # 3. No NaN in critical columns
        # 4. Date formats valid
        pass

# PROCESSORS/core/validators/output_validator.py
class OutputValidator:
    def validate_metrics(self, df: pd.DataFrame, entity_type: str):
        """Validate calculated metrics"""
        # 1. ROE between -1 and 1
        # 2. No infinite values
        # 3. Required columns present
        pass
```

**Usage trong pipeline:**
```python
# PROCESSORS/pipelines/quarterly_report.py
from PROCESSORS.core.validators import InputValidator, OutputValidator

def run_quarterly_pipeline():
    # Step 1: Validate input
    validator = InputValidator()
    validator.validate_csv(raw_csv_path, "BANK")

    # Step 2: Process
    calculator = BankFinancialCalculator()
    result_df = calculator.calculate_all_metrics()

    # Step 3: Validate output
    output_validator = OutputValidator()
    output_validator.validate_metrics(result_df, "BANK")

    # Step 4: Save
    result_df.to_parquet(output_path)
```

---

## 🎯 ĐỀ XUẤT CẢI TIẾN

### Ưu tiên 1: 🔴 CRITICAL (Làm ngay)

#### Fix 1.1: Tách rõ Raw vs Refined Data
**Thời gian:** 2-3 giờ
**Tác động:** Cao - Loại bỏ confusion về data flow

```bash
# Step 1: Rename processed → refined
mv DATA/processed DATA/refined

# Step 2: Restructure raw/
mkdir -p DATA/raw/fundamental/csv/{Q3_2025,Q4_2025}
mkdir -p DATA/raw/market/ohlcv_raw
mkdir -p DATA/raw/macro/csv

# Step 3: Move CSV files to correct location
find DATA/raw/fundamental/processed -name "*.csv" \
  -exec mv {} DATA/raw/fundamental/csv/Q3_2025/ \;

# Step 4: Move parquet to refined/
find DATA/raw/fundamental/processed -name "*.parquet" \
  -exec mv {} DATA/refined/fundamental/current/ \;

# Step 5: Update paths.py
# Change: DATA_DIR / "processed" → DATA_DIR / "refined"
```

**Validation:**
```bash
# Verify structure
ls DATA/raw/fundamental/csv/Q3_2025/  # Should have *.csv only
ls DATA/refined/fundamental/current/  # Should have *.parquet
```

---

#### Fix 1.2: Consolidate Schemas
**Thời gian:** 1-2 giờ
**Tác động:** Cao - Single source of truth

```bash
# Step 1: Create unified schema directory
mkdir -p config/schemas/{data,validation,display}

# Step 2: Move all schemas
mv DATA/schemas/ohlcv*.json config/schemas/data/
mv DATA/schemas/display/*.json config/schemas/display/

# Step 3: Create SchemaRegistry class
cat > PROCESSORS/core/registries/schema_registry.py << 'EOF'
from pathlib import Path
import json

class SchemaRegistry:
    def __init__(self):
        self.schema_dir = Path(__file__).parents[3] / "config" / "schemas"

    def get_data_schema(self, name: str):
        return self._load_schema("data", name)

    def get_validation_schema(self, name: str):
        return self._load_schema("validation", name)

    def _load_schema(self, category: str, name: str):
        schema_path = self.schema_dir / category / f"{name}.json"
        with open(schema_path) as f:
            return json.load(f)

# Global instance
schema_registry = SchemaRegistry()
EOF

# Step 4: Update all imports
find PROCESSORS WEBAPP -name "*.py" -type f \
  -exec sed -i '' 's/from.*schemas import/from PROCESSORS.core.registries.schema_registry import schema_registry/g' {} \;
```

**Validation:**
```bash
# Test schema loading
python3 -c "
from PROCESSORS.core.registries.schema_registry import schema_registry
schema = schema_registry.get_data_schema('ohlcv')
print('✅ Schema loaded:', list(schema.keys()))
"
```

---

### Ưu tiên 2: 🟡 HIGH (Làm trong tuần)

#### Fix 2.1: Create Extractors Layer
**Thời gian:** 4-6 giờ
**Tác động:** Trung bình - Cải thiện code reusability

```bash
# Step 1: Create extractors directory
mkdir -p PROCESSORS/extractors

# Step 2: Extract data loading logic
cat > PROCESSORS/extractors/csv_loader.py << 'EOF'
from pathlib import Path
import pandas as pd
from PROCESSORS.core.config.paths import DATA_DIR

class CSVLoader:
    def __init__(self):
        self.raw_dir = DATA_DIR / "raw"

    def load_fundamental_csv(self, entity_type: str, quarter: str, year: int):
        """Load raw fundamental CSV"""
        csv_dir = self.raw_dir / "fundamental" / "csv" / f"Q{quarter}_{year}"

        entity_files = {
            "COMPANY": "COMPANY_BALANCE_SHEET.csv",
            "BANK": "BANK_BALANCE_SHEET.csv",
            "INSURANCE": "INSURANCE_BALANCE_SHEET.csv",
            "SECURITY": "SECURITY_BALANCE_SHEET.csv"
        }

        csv_path = csv_dir / entity_files[entity_type]
        return pd.read_csv(csv_path)
EOF

# Step 3: Refactor calculators to use loader
# In PROCESSORS/fundamental/calculators/company_calculator.py:
# Replace:
#   df = pd.read_csv("/path/to/csv")
# With:
#   from PROCESSORS.extractors.csv_loader import CSVLoader
#   loader = CSVLoader()
#   df = loader.load_fundamental_csv("COMPANY", quarter, year)
```

---

#### Fix 2.2: Add Validation Layer
**Thời gian:** 6-8 giờ
**Tác động:** Cao - Ngăn data quality issues

```bash
# Step 1: Create validators
mkdir -p PROCESSORS/core/validators

# Step 2: Input validator
cat > PROCESSORS/core/validators/input_validator.py << 'EOF'
import pandas as pd
from pathlib import Path
from typing import List, Optional

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors

class InputValidator:
    def validate_csv(self, csv_path: Path, entity_type: str) -> ValidationResult:
        errors = []

        # 1. File exists
        if not csv_path.exists():
            errors.append(f"File not found: {csv_path}")
            return ValidationResult(False, errors)

        # 2. Load CSV
        df = pd.read_csv(csv_path)

        # 3. Required columns
        required_cols = ["ticker", "year", "quarter", "lengthReport"]
        missing = set(required_cols) - set(df.columns)
        if missing:
            errors.append(f"Missing columns: {missing}")

        # 4. No NaN in critical columns
        if df["ticker"].isna().any():
            errors.append("NaN values in ticker column")

        return ValidationResult(len(errors) == 0, errors)
EOF

# Step 3: Output validator
cat > PROCESSORS/core/validators/output_validator.py << 'EOF'
import pandas as pd

class OutputValidator:
    def validate_metrics(self, df: pd.DataFrame, entity_type: str):
        errors = []

        # 1. ROE sanity check
        if "roe" in df.columns:
            if (df["roe"].abs() > 1.0).any():
                errors.append("ROE > 100% detected")

        # 2. No infinite values
        if df.select_dtypes(include=["float64"]).isin([float("inf"), float("-inf")]).any().any():
            errors.append("Infinite values detected")

        return ValidationResult(len(errors) == 0, errors)
EOF
```

---

#### Fix 2.3: Create Unified Pipeline
**Thời gian:** 3-4 giờ
**Tác động:** Cao - One-command execution

```bash
# Step 1: Create pipelines directory (nếu chưa có)
mkdir -p PROCESSORS/pipelines

# Step 2: Quarterly pipeline
cat > PROCESSORS/pipelines/quarterly_report.py << 'EOF'
#!/usr/bin/env python3
"""
Quarterly Financial Report Pipeline
Runs all fundamental calculators for a given quarter
"""
import argparse
from PROCESSORS.fundamental.calculators import (
    CompanyFinancialCalculator,
    BankFinancialCalculator,
    InsuranceFinancialCalculator,
    SecurityFinancialCalculator
)
from PROCESSORS.core.validators import InputValidator, OutputValidator

def run_quarterly_pipeline(quarter: int, year: int):
    calculators = [
        ("COMPANY", CompanyFinancialCalculator()),
        ("BANK", BankFinancialCalculator()),
        ("INSURANCE", InsuranceFinancialCalculator()),
        ("SECURITY", SecurityFinancialCalculator())
    ]

    for entity_type, calculator in calculators:
        print(f"Processing {entity_type}...")

        # 1. Validate input
        input_validator = InputValidator()
        # ... validation logic

        # 2. Calculate
        result_df = calculator.calculate_all_metrics()

        # 3. Validate output
        output_validator = OutputValidator()
        # ... validation logic

        # 4. Save
        print(f"✅ {entity_type} complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarter", type=int, required=True)
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()

    run_quarterly_pipeline(args.quarter, args.year)
EOF

chmod +x PROCESSORS/pipelines/quarterly_report.py
```

**Usage:**
```bash
# Run quarterly update with one command
python3 PROCESSORS/pipelines/quarterly_report.py --quarter 3 --year 2025
```

---

### Ưu tiên 3: 🟢 MEDIUM (Làm khi rảnh)

#### Fix 3.1: Rename processed → refined
**Thời gian:** 30 phút
**Tác động:** Thấp - Chỉ cải thiện naming clarity

```bash
# Simple rename
mv DATA/processed DATA/refined

# Update paths.py
sed -i '' 's/processed/refined/g' PROCESSORS/core/config/paths.py

# Update all imports
find PROCESSORS WEBAPP -name "*.py" \
  -exec sed -i '' 's/processed/refined/g' {} \;
```

---

#### Fix 3.2: Extract Transformers Layer
**Thời gian:** 8-12 giờ
**Tác động:** Trung bình - Cải thiện testability

Tách calculation logic thành pure functions:

```python
# PROCESSORS/transformers/financial/company_ratios.py
def calculate_roe(net_income: float, equity: float) -> float:
    """Pure function: Calculate ROE"""
    if equity == 0:
        return 0.0
    return net_income / equity

def calculate_roa(net_income: float, assets: float) -> float:
    """Pure function: Calculate ROA"""
    if assets == 0:
        return 0.0
    return net_income / assets
```

Sử dụng trong calculator:
```python
# PROCESSORS/fundamental/calculators/company_calculator.py
from PROCESSORS.transformers.financial.company_ratios import calculate_roe, calculate_roa

class CompanyFinancialCalculator:
    def calculate_all_metrics(self):
        df = self.load_data()

        # Use pure functions
        df["roe"] = df.apply(lambda row: calculate_roe(row["net_income"], row["equity"]), axis=1)
        df["roa"] = df.apply(lambda row: calculate_roa(row["net_income"], row["assets"]), axis=1)

        return df
```

---

## 📋 MIGRATION ROADMAP

### Week 1: Critical Fixes (Làm ngay)
| Task | Thời gian | Priority | Status |
|------|-----------|----------|--------|
| Tách Raw vs Refined data | 2-3h | 🔴 CRITICAL | ⏳ |
| Consolidate schemas | 1-2h | 🔴 CRITICAL | ⏳ |
| Update paths.py | 30m | 🔴 CRITICAL | ⏳ |
| Test imports | 30m | 🔴 CRITICAL | ⏳ |

### Week 2: Validation & Pipelines
| Task | Thời gian | Priority | Status |
|------|-----------|----------|--------|
| Create InputValidator | 3-4h | 🟡 HIGH | ⏳ |
| Create OutputValidator | 3-4h | 🟡 HIGH | ⏳ |
| Create quarterly_pipeline.py | 3-4h | 🟡 HIGH | ⏳ |
| Create extractors layer | 4-6h | 🟡 HIGH | ⏳ |

### Week 3-4: Optional Improvements
| Task | Thời gian | Priority | Status |
|------|-----------|----------|--------|
| Extract transformers layer | 8-12h | 🟢 MEDIUM | ⏳ |
| Add comprehensive tests | 8-12h | 🟢 MEDIUM | ⏳ |
| Documentation update | 4-6h | 🟢 MEDIUM | ⏳ |

---

## 🎯 SUCCESS CRITERIA

### Data Quality ✅
- [ ] 100% separation: raw data vs refined data
- [ ] No processed files in `DATA/raw/`
- [ ] No raw files in `DATA/refined/`
- [ ] Clear quarterly organization in `DATA/raw/fundamental/csv/`

### Code Quality ✅
- [ ] Single schema location: `config/schemas/`
- [ ] SchemaRegistry working across all modules
- [ ] All imports use `PROCESSORS.core.registries.schema_registry`
- [ ] Validation pipeline integrated

### Architecture ✅
- [ ] Extractors layer created
- [ ] Validators working (input + output)
- [ ] Unified quarterly pipeline functional
- [ ] One-command execution working

### Backward Compatibility ✅
- [ ] All existing scripts still work
- [ ] WEBAPP can load data from new locations
- [ ] No breaking changes to public APIs

---

## 🚀 QUICK START GUIDE

### Option 1: Làm từng bước (Recommended)

```bash
# Week 1 - Day 1: Fix data structure
cd /Users/buuphan/Dev/Vietnam_dashboard

# Backup first
git tag v3.0-before-canonical
git checkout -b canonical-structure-migration

# Step 1: Rename processed → refined
mv DATA/processed DATA/refined
sed -i '' 's/DATA\/processed/DATA\/refined/g' PROCESSORS/core/config/paths.py

# Step 2: Restructure raw/
mkdir -p DATA/raw/fundamental/csv/{Q3_2025,Q4_2025}
find DATA/raw/fundamental/processed -name "*.csv" -exec mv {} DATA/raw/fundamental/csv/Q3_2025/ \;
find DATA/raw/fundamental/processed -name "*.parquet" -exec mv {} DATA/refined/fundamental/current/ \;

# Step 3: Test
python3 -c "from PROCESSORS.core.config.paths import REFINED_DIR; print('✅ Paths OK')"

# Commit
git add .
git commit -m "fix: Restructure DATA/ to canonical (raw vs refined)"
```

```bash
# Week 1 - Day 2: Consolidate schemas
mkdir -p config/schemas/{data,validation,display}
mv DATA/schemas/*.json config/schemas/data/

# Create SchemaRegistry
# (Copy code from Fix 1.2 above)

# Test
python3 -c "from PROCESSORS.core.registries.schema_registry import schema_registry; print('✅ Registry OK')"

# Commit
git add .
git commit -m "feat: Consolidate schemas to config/schemas/"
```

---

### Option 2: Script tự động (Nhanh hơn)

```bash
# Run migration script
python3 docs/scripts/migrate_to_canonical.py --dry-run  # Preview changes
python3 docs/scripts/migrate_to_canonical.py --execute   # Apply changes
```

**Note:** Script này sẽ được tạo nếu bạn muốn automate toàn bộ migration.

---

## 📞 KẾT LUẬN

### Điểm mạnh hiện tại:
- ✅ **70% canonical compliance** - Nền tảng tốt
- ✅ **Clean structure** - No technical debt
- ✅ **Proper packages** - Professional Python project
- ✅ **Centralized paths** - Portable code

### Cần cải thiện:
- 🔴 **Raw vs Refined separation** - Critical fix (2-3h)
- 🔴 **Schema consolidation** - Critical fix (1-2h)
- 🟡 **Validation layer** - Important (6-8h)
- 🟡 **Unified pipelines** - Important (3-4h)
- 🟢 **Extractors/Transformers** - Nice to have (12-18h)

### Timeline đề xuất:
- **Week 1:** Critical fixes (4-5h total) → **80% canonical**
- **Week 2:** Validation + pipelines (10-12h) → **90% canonical**
- **Week 3-4:** Extractors + transformers (optional) → **100% canonical**

### Recommendation:
**Làm Week 1 ngay (4-5 giờ).** Đây là những fix có tác động cao nhất với effort thấp nhất. Week 2-4 có thể làm dần khi rảnh.

---

**Ngày đánh giá:** 2025-12-08
**Người đánh giá:** Claude Code
**File tham khảo:**
- `/Users/buuphan/Dev/Vietnam_dashboard/CURRENT_STATUS.md`
- `/Users/buuphan/Dev/Vietnam_dashboard/docs/CANONICAL_STRUCTURE_AND_IMPROVEMENTS.md`
