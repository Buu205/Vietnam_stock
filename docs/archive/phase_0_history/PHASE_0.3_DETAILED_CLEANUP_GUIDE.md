# 📋 PHASE 0.3 - DETAILED CLEANUP GUIDE
## Chi tiết từng thư mục - Xóa gì, Giữ gì, Test thế nào

**Created:** 2025-12-07
**Status:** 🔴 **ACTION REQUIRED - Follow Step by Step**

---

## 📊 CURRENT STATE - What We Have Now

### ✅ NEW Structure (v3.0) - KEEP THESE
```
DATA/                   1.1GB    ← NEW: All data centralized
├── raw/               253MB    ← FROM: data_warehouse/raw/
├── processed/         834MB    ← FROM: calculated_results/
├── metadata/          864KB    ← FROM: data_warehouse/metadata/
└── schemas/           100KB    ← FROM: calculated_results/schemas/ + data_warehouse/schemas/

PROCESSORS/            9.9MB    ← NEW: All processing logic
├── core/                       ← FROM: data_processor/core/
├── fundamental/                ← FROM: data_processor/fundamental/base/
├── technical/                  ← FROM: data_processor/technical/
├── valuation/                  ← FROM: data_processor/valuation/
├── news/                       ← FROM: data_processor/news/
└── forecast/                   ← FROM: data_processor/Bsc_forecast/

WEBAPP/                         ← FROM: streamlit_app/ (renamed)
CONFIG/                         ← KEEP (already clean)
logs/                           ← KEEP (centralized)
archive/                        ← KEEP (v1.0 deprecated code)
```

### ❌ OLD Structure (v2.0) - DELETE THESE
```
data_warehouse/        335MB    ❌ DELETE (duplicated in DATA/)
calculated_results/    834MB    ❌ DELETE (duplicated in DATA/processed/)
data_processor/        9.9MB    ❌ DELETE (duplicated in PROCESSORS/)
streamlit_app/                  ❌ DELETE (renamed to WEBAPP/)
mcp_server/                     ❌ DELETE (renamed to MCP/ if exists)
```

---

## 🔍 DETAILED DIRECTORY AUDIT

### 1. data_warehouse/ (335MB) - CAN DELETE

**What's inside:**
```bash
data_warehouse/
├── raw/                     ✅ COPIED → DATA/raw/
│   ├── ohlcv/              (OHLCV_mktcap.parquet - 164MB)
│   ├── fundamental/        (Material Q3 CSVs)
│   ├── commodity/
│   ├── macro/
│   └── ...
├── metadata/                ✅ COPIED → DATA/metadata/
│   ├── metric_registry.json
│   ├── sector_industry_registry.json
│   └── ...
├── schemas/                 ✅ MERGED → DATA/schemas/
│   ├── ohlcv_schema.json   (merged with ohlcv_data_schema.json)
│   └── ...
└── cache/                   ⚠️ OPTIONAL (can regenerate)
```

**Verification Command:**
```bash
# Verify all raw data copied
diff -r data_warehouse/raw/ DATA/raw/ --brief

# Verify all metadata copied
diff -r data_warehouse/metadata/ DATA/metadata/ --brief
```

**Safe to Delete:** ✅ YES (after verification)

---

### 2. calculated_results/ (834MB) - CAN DELETE

**What's inside:**
```bash
calculated_results/
├── fundamental/             ✅ COPIED → DATA/processed/fundamental/
│   ├── company/            (company_financial_metrics.parquet)
│   ├── bank/               (bank_financial_metrics.parquet)
│   ├── insurance/          (insurance_financial_metrics.parquet)
│   └── security/           (security_financial_metrics.parquet)
├── technical/               ✅ COPIED → DATA/processed/technical/
│   ├── basic_data.parquet
│   ├── moving_averages.parquet
│   ├── rsi.parquet
│   └── ...
├── valuation/               ✅ COPIED → DATA/processed/valuation/
│   ├── stock_pe_pb.parquet
│   └── ...
├── commodity/               ✅ COPIED → DATA/processed/commodity/
├── macro/                   ✅ COPIED → DATA/processed/macro/
└── schemas/                 ✅ MERGED → DATA/schemas/
    ├── ohlcv_data_schema.json
    ├── fundamental_calculated_schema.json
    └── ...
```

**Verification Command:**
```bash
# Verify all parquet files copied
find calculated_results -name "*.parquet" | wc -l
find DATA/processed -name "*.parquet" | wc -l
# Should be equal (102 files each)

# Check file sizes match
du -sh calculated_results/
du -sh DATA/processed/
# Should be ~834MB each
```

**Safe to Delete:** ✅ YES (after verification)

---

### 3. data_processor/ (9.9MB, 71 Python files) - NEEDS CAREFUL REVIEW

**What's inside:**
```bash
data_processor/
├── core/                    ✅ COPIED → PROCESSORS/core/shared/
│   ├── unified_mapper.py
│   ├── ohlcv_formatter.py  → MOVED to PROCESSORS/core/formatters/
│   ├── metric_lookup.py    → MOVED to PROCESSORS/core/registries/
│   └── ...
├── fundamental/
│   ├── base/                ✅ COPIED → PROCESSORS/fundamental/calculators/
│   │   ├── company_financial_calculator.py → company_calculator.py
│   │   ├── bank_financial_calculator.py → bank_calculator.py
│   │   └── ...
│   ├── company/             ⚠️ OLD VERSION (archived)
│   ├── bank/                ⚠️ OLD VERSION (archived)
│   ├── insurance/           ⚠️ OLD VERSION (archived)
│   └── security/            ⚠️ OLD VERSION (archived)
├── technical/
│   ├── ohlcv/               ✅ COPIED → PROCESSORS/technical/ohlcv/
│   ├── indicators/          ✅ COPIED → PROCESSORS/technical/indicators/
│   ├── commodity/           ✅ COPIED → PROCESSORS/technical/commodity/
│   ├── macro/               ✅ COPIED → PROCESSORS/technical/macro/
│   ├── daily_*.py           ✅ COPIED → PROCESSORS/technical/pipelines/
│   └── technical/           ⚠️ OLD NESTED (empty after flattening)
├── valuation/
│   ├── core/                ✅ COPIED → PROCESSORS/valuation/calculators/
│   └── daily_full_valuation_pipeline.py ✅ COPIED → PROCESSORS/valuation/pipelines/
├── news/                    ✅ COPIED → PROCESSORS/news/
└── Bsc_forecast/            ✅ COPIED → PROCESSORS/forecast/
```

**⚠️ CRITICAL FILES - DO NOT DELETE YET:**
```bash
data_processor/fundamental/base/
# These are Phase 0.2 calculators - ALREADY COPIED to PROCESSORS/
# But let's verify they work from new location first
```

**Verification Steps:**

**Step 1: Test PROCESSORS imports work**
```bash
# Test core imports
python3 -c "from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper; print('✅ Core works')"

# Test formatters
python3 -c "from PROCESSORS.core.formatters.ohlcv_formatter import OHLCVFormatter; print('✅ Formatters work')"

# Test registries
python3 -c "from PROCESSORS.core.registries.metric_lookup import MetricRegistry; print('✅ Registries work')"
```

**Step 2: Test fundamental calculators**
```bash
# Test company calculator
python3 -c "from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator; print('✅ Company calculator works')"

# Test bank calculator
python3 -c "from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator; print('✅ Bank calculator works')"
```

**Step 3: Test technical processors**
```bash
# Test technical processor
python3 -c "from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor; print('✅ Technical processor works')"
```

**Safe to Delete:** ⚠️ ONLY AFTER ALL TESTS PASS

---

### 4. streamlit_app/ - ALREADY RENAMED

**Status:** ✅ RENAMED to WEBAPP/
```bash
ls -d WEBAPP/  # Should exist
ls -d streamlit_app/  # Should NOT exist (already renamed)
```

**No action needed** - already handled

---

### 5. mcp_server/ - CHECK IF EXISTS

**Status:** May or may not exist
```bash
ls -d mcp_server/ 2>/dev/null || echo "Not found (OK)"
ls -d MCP/ 2>/dev/null || echo "Not found (OK)"
```

**Action:** If mcp_server/ exists, rename to MCP/

---

## 🎯 STEP-BY-STEP CLEANUP PLAN

### PHASE 1: VERIFICATION (30 minutes)

#### Step 1.1: Verify DATA/ migration
```bash
# Check data sizes match
echo "Checking raw data..."
du -sh data_warehouse/raw
du -sh DATA/raw
# Should be similar (253MB)

echo "Checking processed data..."
du -sh calculated_results/
du -sh DATA/processed/
# Should be similar (834MB)

echo "Checking metadata..."
du -sh data_warehouse/metadata
du -sh DATA/metadata
# Should be similar (864KB)

echo "Counting parquet files..."
find calculated_results -name "*.parquet" | wc -l
find DATA/processed -name "*.parquet" | wc -l
# Should be equal (102 files)
```

**Expected Result:** All sizes match ✅

#### Step 1.2: Verify PROCESSORS/ migration
```bash
# Test all critical imports
python3 << 'EOF'
try:
    from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
    from PROCESSORS.core.formatters.ohlcv_formatter import OHLCVFormatter
    from PROCESSORS.core.registries.metric_lookup import MetricRegistry
    print("✅ Core imports work")
except Exception as e:
    print(f"❌ Core imports failed: {e}")

try:
    from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
    print("✅ Fundamental imports work")
except Exception as e:
    print(f"❌ Fundamental imports failed: {e}")

try:
    from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor
    print("✅ Technical imports work")
except Exception as e:
    print(f"❌ Technical imports failed: {e}")
EOF
```

**Expected Result:** All imports work ✅

**If imports fail:** Do NOT proceed to deletion. Fix imports first.

---

### PHASE 2: CREATE BACKUP (10 minutes)

**BEFORE deleting anything, create backup:**

```bash
# Create backup tarball
tar -czf backup_old_structure_$(date +%Y%m%d_%H%M%S).tar.gz \
    data_warehouse/ \
    calculated_results/ \
    data_processor/ \
    2>/dev/null

# Verify backup created
ls -lh backup_old_structure_*.tar.gz

# Should see file ~1.1GB (compressed)
```

**Expected Result:** Backup file created ✅

---

### PHASE 3: SAFE DELETION (15 minutes)

**⚠️ ONLY proceed if Phase 1 & 2 passed!**

#### Step 3.1: Delete data_warehouse/ (335MB)
```bash
# Verify one more time
diff -r data_warehouse/raw/ DATA/raw/ --brief
diff -r data_warehouse/metadata/ DATA/metadata/ --brief

# If no differences, safe to delete
rm -rf data_warehouse/

# Verify deleted
ls -d data_warehouse/ 2>/dev/null && echo "❌ Still exists!" || echo "✅ Deleted"
```

#### Step 3.2: Delete calculated_results/ (834MB)
```bash
# Verify parquet count
find calculated_results -name "*.parquet" | wc -l
find DATA/processed -name "*.parquet" | wc -l

# If counts match, safe to delete
rm -rf calculated_results/

# Verify deleted
ls -d calculated_results/ 2>/dev/null && echo "❌ Still exists!" || echo "✅ Deleted"
```

#### Step 3.3: Delete data_processor/ (9.9MB)
```bash
# FINAL CHECK: Test imports work from PROCESSORS/
python3 -c "from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator; print('✅ Ready to delete')"

# If test passes, safe to delete
rm -rf data_processor/

# Verify deleted
ls -d data_processor/ 2>/dev/null && echo "❌ Still exists!" || echo "✅ Deleted"
```

---

### PHASE 4: VERIFY CLEAN STATE (5 minutes)

```bash
# Check new structure
echo "=== NEW STRUCTURE (v3.0) ==="
ls -d DATA/ PROCESSORS/ WEBAPP/ CONFIG/
echo ""

# Check sizes
echo "=== DATA SIZES ==="
du -sh DATA/raw DATA/processed DATA/metadata
echo ""

# Check old folders deleted
echo "=== OLD FOLDERS (should not exist) ==="
ls -d data_warehouse/ 2>/dev/null && echo "❌ data_warehouse still exists" || echo "✅ data_warehouse deleted"
ls -d calculated_results/ 2>/dev/null && echo "❌ calculated_results still exists" || echo "✅ calculated_results deleted"
ls -d data_processor/ 2>/dev/null && echo "❌ data_processor still exists" || echo "✅ data_processor deleted"
echo ""

# Final test: Import from new structure
python3 -c "from PROCESSORS.core.config.paths import DATA_ROOT, PROCESSORS_ROOT; print(f'✅ Paths work: DATA={DATA_ROOT}')"
```

**Expected Output:**
```
=== NEW STRUCTURE (v3.0) ===
DATA/  PROCESSORS/  WEBAPP/  CONFIG/

=== DATA SIZES ===
253M    DATA/raw
834M    DATA/processed
864K    DATA/metadata

=== OLD FOLDERS (should not exist) ===
✅ data_warehouse deleted
✅ calculated_results deleted
✅ data_processor deleted

✅ Paths work: DATA=.../stock_dashboard/DATA
```

---

## 🧪 TESTING PLAN - Verify Everything Works

### Test 1: Paths Configuration
```bash
python3 PROCESSORS/core/config/paths.py
```

**Expected:** Should print all paths correctly

### Test 2: Import New Calculators
```bash
python3 << 'EOF'
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
print("✅ All calculators import successfully")
EOF
```

### Test 3: Load Data from New Paths
```bash
python3 << 'EOF'
from PROCESSORS.core.config.paths import DATA_ROOT, PROCESSED_FUNDAMENTAL
import pandas as pd

# Try to load company metrics
company_file = PROCESSED_FUNDAMENTAL / "company" / "company_financial_metrics.parquet"
df = pd.read_parquet(company_file)
print(f"✅ Loaded company metrics: {len(df)} rows, {len(df.columns)} columns")

# Try to load bank metrics
bank_file = PROCESSED_FUNDAMENTAL / "bank" / "bank_financial_metrics.parquet"
df = pd.read_parquet(bank_file)
print(f"✅ Loaded bank metrics: {len(df)} rows, {len(df.columns)} columns")
EOF
```

**Expected:**
```
✅ Loaded company metrics: XXXX rows, XX columns
✅ Loaded bank metrics: XXXX rows, XX columns
```

### Test 4: Run a Simple Calculator (Dry Run)
```bash
# This will test if calculators can access new DATA/ paths
python3 << 'EOF'
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.core.config.paths import RAW_FUNDAMENTAL, PROCESSED_FUNDAMENTAL

# Initialize calculator
calc = CompanyFinancialCalculator()

# Check if it can find raw data
print(f"Raw data path: {RAW_FUNDAMENTAL}")
print(f"Output path: {PROCESSED_FUNDAMENTAL}")
print("✅ Calculator initialized successfully")
EOF
```

---

## 🚨 ROLLBACK PLAN (If Something Goes Wrong)

### If Tests Fail After Deletion

**Step 1: Stop immediately**
```bash
# Do NOT delete more folders if any test fails
```

**Step 2: Restore from backup**
```bash
# Find your backup
ls -lh backup_old_structure_*.tar.gz

# Extract backup
tar -xzf backup_old_structure_YYYYMMDD_HHMMSS.tar.gz

# Verify restored
ls -d data_warehouse/ calculated_results/ data_processor/
```

**Step 3: Report issue**
- Note which test failed
- Check error message
- Review import paths

---

## 📅 RECOMMENDED EXECUTION SCHEDULE

### Option A: Careful Approach (Recommended)
```
Day 1 Morning:   Phase 1 - Verification (30 min)
Day 1 Afternoon: Phase 2 - Create Backup (10 min)
                 Phase 3 - Delete data_warehouse/ only (5 min)
                 Test everything still works (15 min)

Day 2 Morning:   Phase 3 - Delete calculated_results/ (5 min)
                 Test everything still works (15 min)

Day 2 Afternoon: Phase 3 - Delete data_processor/ (5 min)
                 Phase 4 - Verify clean state (5 min)
                 Full system test (30 min)
```

### Option B: Quick Approach (If confident)
```
Same Day:
1. Phase 1 - Verification (30 min)
2. Phase 2 - Backup (10 min)
3. Phase 3 - Delete all old folders (15 min)
4. Phase 4 - Verify + Test (40 min)

Total: ~2 hours
```

---

## ✅ SUCCESS CRITERIA

After cleanup, you should have:

### Directory Structure
```
✅ DATA/ exists (1.1GB)
   ├── raw/ (253MB)
   ├── processed/ (834MB)
   ├── metadata/ (864KB)
   └── schemas/ (100KB)

✅ PROCESSORS/ exists (9.9MB)
   ├── core/
   ├── fundamental/
   ├── technical/
   ├── valuation/
   ├── news/
   └── forecast/

✅ WEBAPP/ exists
✅ CONFIG/ exists

❌ data_warehouse/ DOES NOT exist
❌ calculated_results/ DOES NOT exist
❌ data_processor/ DOES NOT exist
```

### Functionality
```
✅ All imports work from PROCESSORS/
✅ Can load data from DATA/
✅ paths.py returns correct paths
✅ Calculators initialize without errors
```

### Backup
```
✅ Backup file exists (~1.1GB compressed)
✅ Can restore from backup if needed
```

---

## 🎯 NEXT STEPS AFTER CLEANUP

### Week 2: Formula Extraction
1. Extract formulas from PROCESSORS/fundamental/calculators/
2. Create PROCESSORS/fundamental/formulas/
3. Separate pure calculation logic from data loading

### Week 3: Pipeline Creation
1. Create quarterly_pipeline.py
2. Test automated parquet generation
3. Validation reports

### Week 4: Documentation
1. Update CLAUDE.md
2. Create docs/INDEX.md
3. Migration guide

---

## 📞 TROUBLESHOOTING

### Issue: Imports fail after migration
**Solution:** Check PYTHONPATH and sys.path
```python
import sys
print(sys.path)
# Should include /Users/buuphan/Dev/stock_dashboard
```

### Issue: Cannot find DATA/ folder
**Solution:** Check paths.py configuration
```python
from PROCESSORS.core.config.paths import DATA_ROOT
print(DATA_ROOT)
# Should be /Users/buuphan/Dev/stock_dashboard/DATA
```

### Issue: Parquet files not found
**Solution:** Verify migration completed
```bash
find DATA/processed -name "*.parquet" | wc -l
# Should be 102 files
```

---

**Document Status:** 🔴 **READY TO EXECUTE**
**Last Updated:** 2025-12-07
**Next Review:** After Phase 3 completion

---

## 📝 EXECUTION CHECKLIST

```
Pre-Cleanup:
[ ] Read this entire document
[ ] Understand each phase
[ ] Set aside 2-3 hours
[ ] Have backup plan ready

Phase 1: Verification
[ ] Check DATA/ sizes match old folders
[ ] Test all PROCESSORS/ imports
[ ] Verify parquet file counts match
[ ] All tests pass ✅

Phase 2: Backup
[ ] Create backup tarball
[ ] Verify backup file exists (>1GB)
[ ] Test can extract backup

Phase 3: Deletion
[ ] Delete data_warehouse/
[ ] Delete calculated_results/
[ ] Delete data_processor/
[ ] Verify all deleted

Phase 4: Verification
[ ] Check new structure exists
[ ] Test imports from PROCESSORS/
[ ] Test loading data from DATA/
[ ] Run calculator dry run
[ ] All tests pass ✅

Post-Cleanup:
[ ] Update git status
[ ] Commit changes
[ ] Ready for Week 2 (Formula Extraction)
```

---

**Ready to proceed! Follow steps carefully. 🚀**
