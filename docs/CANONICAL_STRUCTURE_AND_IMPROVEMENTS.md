# 🏗️ VIETNAM DASHBOARD - CẤU TRÚC CHUẨN VÀ ĐỀ XUẤT CẢI TIẾN

**Ngày:** 2025-12-08
**Phiên bản:** 2.0 - Updated with actual evaluation
**Trạng thái:** ✅ 70% Canonical Compliance → Roadmap to 100%

> **TL;DR:** Dự án đã đạt **70% canonical compliance**. Cần **5 cải tiến chiến thuật** (4-5h effort) để đạt 100%.
> Chi tiết đánh giá thực tế: `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md`

---

## 📊 CẤU TRÚC CHUẨN (Canonical Structure)

### 1. Tổng quan hệ thống
```
Vietnam_dashboard/
│
├── 1. DATA/                          # [DATA LAYER] - Dữ liệu (READ ONLY)
│   ├── raw/                        # Dữ liệu thô từ nguồn
│   │   ├── fundamental/csv/           # BCTC từ BSC
│   │   ├── market/ohlcv/             # Giá khốiớp, OHLCV
│   │   └── macro/                    # Lãi suất, tỷ giá
│   │
│   ├── refined/                     # Dữ liệu đã xử lý (OUTPUT)
│   │   ├── fundamental/              # Metrics tài chính
│   │   ├── technical/               # Technical indicators
│   │   └── valuation/               # PE/PB ratios
│   │
│   └── schemas/                     # Schema và validation
│       ├── input_validation/         # Schema cho raw data
│       └── output_validation/        # Schema cho refined data
│
├── 2. PROCESSING/                   # [LOGIC LAYER] - Xử lý dữ liệu
│   ├── core/                       # Utilities và config
│   │   ├── config.py                # Class Config quản lý settings
│   │   ├── paths.py                 # Quản lý đường dẫn data
│   │   └── logger.py                # Cấu hình logging
│   │
│   ├── extractors/                  # Đọc dữ liệu từ nguồn
│   │   ├── csv_loader.py            # Đọc BCTC CSV
│   │   └── api_loader.py            # Đọc từ API
│   │
│   ├── transformers/               # Logic tính toán chính
│   │   ├── financial/               # Financial ratios
│   │   ├── technical/              # Technical indicators
│   │   └── valuation/              # Valuation models
│   │
│   └── pipelines/                  # Orchestrator scripts
│       ├── daily_update.py          # Chạy hàng ngày
│       └── quarterly_report.py      # Chạy khi có BCTC
│
├── 3. WEBAPP/                        # [PRESENTATION LAYER] - Giao diện
│   ├── pages/                      # Dashboard pages
│   ├── components/                  # UI tái sử dụng
│   ├── services/                   # Data fetching logic
│   └── assets/                     # CSS, images
│
├── 4. CONFIG/                        # Cấu hình hệ thống
├── 5. TESTS/                         # Kiểm thử
└── 6. SCRIPTS/                       # Scripts tiện ích
```

### 2. Luồng dữ liệu một chiều
```
RAW DATA → PROCESSING → REFINED DATA → WEBAPP
   ↑           ↑              ↑            ↑
 READ ONLY   READ/WRITE    READ ONLY   READ ONLY
```

---

## ✅ ĐÁNH GIÁ THỰC TẾ DỰ ÁN

### Trạng thái hiện tại: 70% Canonical Compliance

| Tiêu chí | Trạng thái | Đánh giá |
|----------|------------|----------|
| Data-Logic Separation | ✅ 100% | DATA/ và PROCESSORS/ tách biệt hoàn hảo |
| Package Structure | ✅ 100% | Đầy đủ `__init__.py`, no sys.path hacks |
| Path Management | ✅ 100% | Centralized trong `PROCESSORS/core/config/paths.py` |
| No Duplication | ✅ 100% | Đã xóa toàn bộ duplicate code (v3.0) |
| Raw vs Processed | 🟡 60% | Cần tách rõ hơn (1 số parquet còn trong raw/) |
| Naming Clarity | 🟡 80% | processed → refined sẽ rõ hơn |
| Schema Location | 🔴 40% | Schema rải rác 3 nơi |
| Pipeline Structure | 🟡 70% | Technical có pipeline, fundamental chưa |
| Validation System | 🔴 30% | Thiếu input/output validators |

**Chi tiết đánh giá:** Xem `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md`

---

## 🐛 CÁC VẤN ĐỀ CẦN SỬA (Từ thực tế dự án)

### 1. Lẫn lộn giữa Raw và Processed Data
**Vấn đề hiện tại:**
- File CSV và Parquet nằm chung trong `DATA/raw/fundamental/processed/`
- Không rõ đâu là input, đâu là output

**Cấu trúc hiện tại:**
```
DATA/raw/fundamental/processed/
├── BANK_BALANCE_SHEET.csv       # Raw
├── bank_full.parquet              # Processed
├── COMPANY_BALANCE_SHEET.csv     # Raw
└── company_full.parquet           # Processed
```

**Cấu trúc đúng:**
```
DATA/raw/fundamental/csv/Q3_2025/
├── BANK_BALANCE_SHEET.csv       # Raw input

DATA/refined/fundamental/current/
├── bank_metrics.parquet          # Processed output
```

### 2. Tên thư mục dễ gây nhầm lẫn
**Vấn đề hiện tại:**
- `PROCESSORS` - Gần với "processors" trong CPU
- `processed` - Trùng động từ "process"

**Tên đúng:**
- `PROCESSING` - Rõ ràng, là danh từ
- `refined` - Rõ ràng là kết quả đã xử lý

### 3. Đường dẫn hardcode tràn lan
**Vấn đề hiện tại:**
```python
# Trong nhiều file
df = pd.read_csv("/Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/fundamental/...")
# ❌ Không portable, không flexible
```

**Cách đúng:**
```python
from PROCESSING.core.paths import DataPaths

paths = DataPaths()
def load_csv():
    csv_path = paths.raw_fundamental_csv / "BANK_BALANCE_SHEET.csv"
    df = pd.read_csv(csv_path)
```

### 4. Thiếu package structure
**Vấn đề hiện tại:**
- Nhiều thư mục thiếu `__init__.py`
- Import phức tạp với `sys.path.insert`

**Cấu trúc đúng:**
- Mọi module có package marker
- Sử dụng relative imports

### 5. Logic phân tán không rõ ràng
**Vấn đề hiện tại:**
- Calculators và transformers lẫn lộn
- Không rõ đâu là pure functions

**Cấu trúc đúng:**
```
PROCESSING/transformers/financial/
├── bank_ratios.py              # Pure calculation functions
├── company_ratios.py           # Pure calculation functions
└── formulas/
    └── base_formulas.py         # Common formulas

PROCESSING/calculators/
├── bank_calculator.py          # Orchestrator, calls pure functions
└── company_calculator.py       # Orchestrator
```

---

## 🎯 ĐỀ XUẤT CẢI TIẾN (CẬP NHẬT THỰC TẾ)

### 📊 Ưu tiên thực tế cho Vietnam Dashboard

**Week 1 (4-5h effort) - 🔴 CRITICAL:**
1. ✅ Tách Raw vs Refined data (2-3h) → Xóa confusion
2. ✅ Consolidate schemas (1-2h) → Single source of truth
3. ✅ Update paths.py (30m) → processed → refined
4. ✅ Test imports (30m) → Verify everything works

**Week 2 (10-12h) - 🟡 HIGH:**
5. Validation layer (6-8h) → Data quality
6. Unified pipelines (3-4h) → One-command execution

**Week 3-4 (12-18h) - 🟢 OPTIONAL:**
7. Extractors layer (4-6h) → Code reusability
8. Transformers layer (8-12h) → Pure functions

---

### 1. Migration Strategy (CẬP NHẬT)
**Phase 1: Data Separation (2-3 giờ - CRITICAL)**
```bash
# Tạo cấu trúc mới
mkdir -p DATA/refined/{fundamental,technical,valuation}
mkdir -p DATA/raw/fundamental/csv/{Q3_2025,Q4_2025}

# Di chuyển file đúng chỗ
mv DATA/raw/fundamental/processed/*.csv DATA/raw/fundamental/csv/Q3_2025/
mv DATA/raw/fundamental/processed/*.parquet DATA/refined/fundamental/
```

**Phase 2: Processing Logic (Ngày 3-4)**
```bash
# Đổi tên và reorganize
mv PROCESSORS PROCESSING

# Tạo cấu trúc chuẩn
mkdir -p PROCESSING/{extractors,transformers,pipelines}
mkdir -p PROCESSING/transformers/{financial,technical,valuation}

# Di chuyển logic đúng chỗ
mv PROCESSING/fundamental/calculators/* PROCESSING/calculators/
mv PROCESSING/technical/indicators/* PROCESSING/transformers/technical/
```

**Phase 3: Path Management (Ngày 5)**
```bash
# Tạo paths.py chuẩn
cat > PROCESSING/core/paths.py << 'EOF'
import os
from pathlib import Path
from typing import Optional

class DataPaths:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(os.environ.get("DATA_DIR", Path.cwd() / "DATA"))
        
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.refined_dir = self.data_dir / "refined"
        
        # Specific paths
        self.raw_fundamental_csv = self.raw_dir / "fundamental" / "csv"
        self.refined_fundamental = self.refined_dir / "fundamental"

# Global instance
paths = DataPaths()
EOF

# Cập nhật imports trong tất cả file
find PROCESSING WEBAPP -name "*.py" -exec sed -i 's/from.*PROCESSORS/from PROCESSING/g' {} \;
```

### 2. Validation Rules
**Input Validation:**
```python
# PROCESSING/extractors/csv_loader.py
from PROCESSING.core.paths import paths
from PROCESSING.core.validators import validate_csv_schema

def load_bank_balance_sheet(quarter: str, year: int):
    csv_path = paths.raw_quarterly_path(quarter, year) / "BANK_BALANCE_SHEET.csv"
    
    # 1. Validate schema
    validation_result = validate_csv_schema(csv_path, "bank_balance_sheet")
    if not validation_result.is_valid:
        raise ValueError(f"Schema validation failed: {validation_result.errors}")
    
    # 2. Load data
    df = pd.read_csv(csv_path)
    return df
```

**Output Validation:**
```python
# PROCESSING/transformers/financial/bank_ratios.py
def calculate_nim(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Business validation
    if df['interest_income'].isna().any():
        raise ValueError("Interest income contains NaN values")
    
    # 2. Calculate ratio
    nim = df['interest_income'] / df['interest_bearing_assets']
    
    # 3. Quality check
    if nim.abs() > 1.0:  # NIM > 100% không hợp lý
        raise ValueError(f"NIM too high: {nim.max()}")
    
    return nim
```

### 3. Testing Strategy
**Unit Tests:**
```python
# TESTS/unit/test_financial_ratios.py
import pytest
from PROCESSING.transformers.financial.bank_ratios import calculate_nim

def test_calculate_nim_normal_case():
    """Test NIM calculation with normal values"""
    # Arrange
    interest_income = 1000.0
    interest_bearing_assets = 50000.0
    
    # Act
    result = calculate_nim(interest_income, interest_bearing_assets)
    
    # Assert
    assert result == 0.02  # 2% NIM
```

---

## 📋 ROADMAP CẢI TIẾN

### 1. Immediate (Priority: 🔴 CRITICAL)
| Task | Thời gian | Owner | Status |
|------|-----------|--------|--------|
| Migration raw → processed | 2 ngày | Data Team | ⏳ |
| Rename PROCESSORS → PROCESSING | 1 ngày | Tech Lead | ⏳ |
| Create standardized paths.py | 1 ngày | Tech Lead | ⏳ |
| Add input/output validation | 2 ngày | QA Team | ⏳ |

### 2. Short Term (Priority: 🟡 HIGH)
| Task | Thời gian | Owner | Status |
|------|-----------|--------|--------|
| Comprehensive unit tests | 1 tuần | Dev Team | ⏳ |
| Pipeline monitoring | 1 tuần | Ops Team | ⏳ |
| Error handling improvement | 3 ngày | Dev Team | ⏳ |
| Documentation update | 2 ngày | Tech Lead | ⏳ |

### 3. Medium Term (Priority: 🟢 MEDIUM)
| Task | Thời gian | Owner | Status |
|------|-----------|--------|--------|
| Performance optimization | 2 tuần | Dev Team | ⏳ |
| Data quality dashboard | 1 tuần | Data Team | ⏳ |
| CI/CD pipeline | 1 tuần | DevOps | ⏳ |

---

## 🎯 SUCCESS CRITERIA

### Data Quality ✅
- [ ] 100% input data validated before processing
- [ ] 100% output data validated after processing
- [ ] Clear separation between raw and refined data
- [ ] Automated data quality monitoring

### Code Quality ✅
- [ ] Zero hardcoded paths
- [ ] 95%+ test coverage
- [ ] All functions have type hints
- [ ] All functions have docstrings

### Architecture ✅
- [ ] Clear separation of concerns
- [ ] No circular imports
- [ ] Package structure complete
- [ ] No sys.path hacks

---

## 📞 IMPLEMENTATION GUIDE

### 1. Migration Commands
```bash
# Backup current state
git tag v1.0-before-cleanup
git checkout -b cleanup-improvements

# Create new structure
mkdir -p DATA/refined/{fundamental,technical,valuation}
mkdir -p DATA/raw/fundamental/csv/{Q3_2025,Q4_2025}

# Move data
find DATA/raw/fundamental/processed -name "*.csv" -exec mv {} DATA/raw/fundamental/csv/Q3_2025/ \;
find DATA/raw/fundamental/processed -name "*.parquet" -exec mv {} DATA/refined/fundamental/ \;

# Update imports
find PROCESSING WEBAPP -name "*.py" -exec sed -i 's/PROCESSORS/PROCESSING/g' {} \;

# Test structure
python -c "from PROCESSING.core.paths import paths; print(paths.raw_dir)"
```

### 2. Validation Implementation
```python
# Add to pipeline
def run_pipeline():
    # Input validation
    validate_input_files()
    
    # Processing
    result = process_data()
    
    # Output validation
    validate_output_data(result)
    
    # Save
    save_to_refined(result)
```

### 3. Testing Implementation
```bash
# Run all tests
pytest TESTS/ --cov=PROCESSING --cov-report=html

# Generate coverage report
open htmlcov/index.html
```

---

## 📞 NEXT STEPS (CẬP NHẬT THỰC TẾ)

### Option 1: Chạy migration script tự động (RECOMMENDED)

```bash
cd /Users/buuphan/Dev/Vietnam_dashboard

# Preview changes
python3 docs/scripts/migrate_to_canonical.py --dry-run

# Apply changes
python3 docs/scripts/migrate_to_canonical.py --execute

# Test
python3 -c "from PROCESSORS.core.registries.schema_registry import schema_registry; print('✅ OK')"
```

**Thời gian:** 15-30 phút (script tự động)

---

### Option 2: Manual migration (từng bước)

Xem chi tiết: `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md` → Section "QUICK START GUIDE"

**Thời gian:** 4-5 giờ (làm thủ công)

---

### Sau khi migrate:

1. **Test imports:**
   ```bash
   python3 PROCESSORS/fundamental/calculators/company_calculator.py
   streamlit run WEBAPP/main.py
   ```

2. **Commit:**
   ```bash
   git add .
   git commit -m "feat: Migrate to canonical structure (70% → 90%)"
   git push
   ```

3. **Next phase:** Validation layer + Unified pipelines (Week 2)

---

## 📚 TÀI LIỆU LIÊN QUAN

- **Chi tiết đánh giá:** `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md` (⭐ ĐỌC NÀY TRƯỚC)
- **Migration script:** `/docs/scripts/migrate_to_canonical.py`
- **Current status:** `/CURRENT_STATUS.md`
- **Claude guide:** `/CLAUDE.md`

---

**Ngày tạo:** 2025-12-08
**Ngày cập nhật:** 2025-12-08 (v2.0 - với đánh giá thực tế)
**Ngày review tiếp theo:** 2025-12-15
**Status:** ✅ Ready to execute (70% → 100% canonical)
