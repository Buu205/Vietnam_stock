# 🎯 REFACTOR MASTERPLAN - Vietnamese Stock Dashboard
**Ngày bắt đầu:** 2025-12-10
**Ước tính:** ~9 giờ | **53 files modified + 34 deleted**

---

## 📊 PROGRESS OVERVIEW

- [ ] **Phase 0**: Pre-flight Cleanup (15 phút)
- [x] **Phase 1**: PROCESSORS/valuation (1 giờ) ✅
- [x] **Phase 2**: PROCESSORS/fundamental (45 phút) ✅
- [x] **Phase 3**: PROCESSORS/technical (1h 15min) ✅
- [x] **Phase 4**: WEBAPP Namespace Fixes (30 phút) ✅
- [ ] **Phase 5**: WEBAPP Schema Registry Integration (2 giờ)
- [ ] **Phase 6**: WEBAPP Data Loading Consolidation (1h 30min)
- [ ] **Phase 7**: Test Files & Documentation (30 phút)
- [ ] **Phase 8**: Final Validation & Testing (1 giờ)

**Completion: 4 / 9 phases** ✅✅✅✅⬜⬜⬜⬜⬜

---

## PHASE 0: Pre-flight Cleanup ⏱️ 15 phút

**Status:** ⬜ Not Started

### Tasks:
- [ ] Delete 3 empty folders (schemas/display, schemas/validation, transformers/technical)
- [ ] Delete 14 backup parquet files (macro + commodity)
- [ ] Delete 2 doc/config backups (README.md.backup, check_single_record.py)
- [ ] Delete empty PROCESSORS/core/registries/ folder

**Files Affected:** 21 items to delete

**Completion:** 0 / 4 tasks

---

## PHASE 1: PROCESSORS/valuation ⏱️ 1 giờ

**Status:** ✅ Completed (2025-12-10)

### Step 1.1: Delete Duplicate Files ✅
- [x] Delete entire PROCESSORS/valuation/core/ folder (5 duplicate files)

### Step 1.2: Update Paths ✅ (6 files)
- [x] calculators/historical_pe_calculator.py
- [x] calculators/historical_pb_calculator.py
- [x] calculators/historical_ev_ebitda_calculator.py
- [x] calculators/bsc_universal_pe_calculator.py
- [x] calculators/vnindex_pe_calculator_optimized.py
- [x] sector_pe_calculator.py

**Pattern:** `data_warehouse/raw` → `DATA/raw`, `calculated_results` → `DATA/processed`

### Step 1.3: Vietnamese Docstrings ✅ (5 files)
- [x] historical_pe_calculator.py
- [x] historical_pb_calculator.py
- [x] historical_ev_ebitda_calculator.py
- [x] vnindex_pe_calculator_optimized.py
- [x] sector_pe_calculator.py

**Completion:** 12 / 12 tasks ✅

**Notes:**
- Đã xóa folder core/ chứa 5 file trùng lặp
- Đã cập nhật import paths từ `date_formatter` → `PROCESSORS.core.shared.date_formatter`
- Đã thêm Vietnamese docstrings cho tất cả các file
- Paths đã đúng sẵn trong hầu hết các file (DATA/raw, DATA/processed)

---

## PHASE 2: PROCESSORS/fundamental ⏱️ 45 phút

**Status:** ✅ Completed (2025-12-10)

### Step 2.1: Delete Duplicates ✅
- [x] Delete entire PROCESSORS/fundamental/base/ folder (5 duplicate files)

### Step 2.2: Fix Imports ✅
- [x] Check for imports from fundamental.base.* (grep)
- [x] Update any found imports to fundamental.calculators.*

### Step 2.3: Vietnamese Docstrings ✅ (4 files)
- [x] calculators/company_calculator.py
- [x] calculators/bank_calculator.py
- [x] calculators/insurance_calculator.py
- [x] calculators/security_calculator.py

**Completion:** 7 / 7 tasks ✅

**Notes:**
- Đã xóa folder base/ chứa 5 file trùng lặp
- Không tìm thấy imports từ fundamental.base cần cập nhật
- Đã thêm Vietnamese docstrings cho tất cả 4 calculator files
- Thời gian thực hiện: ~30 phút

---

## PHASE 3: PROCESSORS/technical ⏱️ 1h 15min

**Status:** ✅ Completed (2025-12-10)

### Step 3.1: Delete Archive ✅
- [x] Delete PROCESSORS/technical/archive/deprecated_v1.0/ folder

### Step 3.2: Update Paths ✅ (8 files)
- [x] indicators/technical_processor.py
- [x] indicators/historical_technical_processor.py
- [x] indicators/stock_screener.py
- [x] indicators/market_breadth_processor.py
- [x] ohlcv/ohlcv_daily_updater.py
- [x] daily_ohlcv_update.py
- [x] macro/macro_data_fetcher.py
- [x] commodity/commodity_price_updater.py

### Step 3.3: Fix Import Fallbacks ✅ (3 files)
- [x] technical_processor.py (remove try/except fallbacks)
- [x] historical_technical_processor.py
- [x] ohlcv_daily_updater.py

### Step 3.4: Vietnamese Docstrings ✅ (6 files)
- [x] indicators/technical_processor.py
- [x] indicators/historical_technical_processor.py
- [x] ohlcv/ohlcv_daily_updater.py
- [x] macro/macro_data_fetcher.py
- [x] commodity/commodity_price_updater.py
- [x] pipelines/daily_technical_pipeline.py

**Completion:** 18 / 18 tasks ✅

**Notes:**
- Đã xóa folder archive/ chứa deprecated_v1.0
- Đã cập nhật paths từ data_warehouse → DATA, calculated_results → DATA/processed
- Đã xóa try/except fallback imports trong 3 files
- Đã thêm Vietnamese docstrings cho 6 files chính
- Thời gian thực hiện: ~50 phút

---

## PHASE 4: WEBAPP - Fix Broken Namespaces ⏱️ 30 phút

**Status:** ✅ Completed (2025-12-10) **Priority:** 🔴 CRITICAL

### Fix streamlit_app → WEBAPP ✅ (3 files)
- [x] WEBAPP/domains/banking/data_loading_bank.py (lines 10-11)
- [x] WEBAPP/pages/news_dashboard.py (lines 7-8)
- [x] WEBAPP/core/data_loading.py (lines 11-12)

**Completion:** 3 / 3 tasks ✅

**Notes:**
- Đã sửa tất cả imports từ `streamlit_app.*` → `WEBAPP.*`
- Các file import errors đã được khắc phục
- Thời gian thực hiện: ~15 phút

---

## PHASE 5: WEBAPP - Schema Registry Integration ⏱️ 2 giờ

**Status:** ⬜ Not Started

### Step 5.1: Update Core Formatters
- [ ] WEBAPP/core/formatters.py (integrate SchemaRegistry)

### Step 5.2: Update Pages (7 files)
- [ ] pages/company_dashboard_pyecharts.py
- [ ] pages/bank_dashboard.py
- [ ] pages/technical_dashboard.py (remove local format_price lines 1592-1620)
- [ ] pages/forecast_dashboard.py
- [ ] pages/securities_dashboard.py
- [ ] pages/valuation_sector_dashboard.py
- [ ] pages/news_dashboard.py

### Step 5.3: Update Domain Loaders (5 files)
- [ ] domains/company/data_loading_company.py
- [ ] domains/banking/data_loading_bank.py
- [ ] domains/technical/data_loading_technical.py
- [ ] domains/forecast/data_loading_forecast.py
- [ ] domains/forecast/data_loading_forecast_csv.py

### Step 5.4: Vietnamese Docstrings (3 files)
- [ ] core/formatters.py
- [ ] core/data_paths.py
- [ ] core/display_config.py

**Completion:** 0 / 16 tasks

---

## PHASE 6: WEBAPP - Data Loading Consolidation ⏱️ 1h 30min

**Status:** ⬜ Not Started

### Step 6.1: Centralize Valuation Loading
- [ ] Create WEBAPP/domains/valuation/data_loading_valuation.py
- [ ] Remove duplicate from company_dashboard_pyecharts.py (lines 96-120)
- [ ] Remove duplicate from data_loading_forecast.py (lines 70-80)

### Step 6.2: Centralize Symbol Loading
- [ ] Create WEBAPP/core/symbol_loader.py
- [ ] Update data_loading_company.py to use it
- [ ] Update data_loading_bank.py to use it
- [ ] Update technical_dashboard.py to use it

### Step 6.3: Update Old Paths (4 files)
- [ ] pages/bank_dashboard.py (8 path refs)
- [ ] pages/company_dashboard_pyecharts.py (5 path refs)
- [ ] pages/technical_dashboard.py (10 path refs)
- [ ] services/commodity_loader.py (4 refs + remove hybrid logic)

**Completion:** 0 / 11 tasks

---

## PHASE 7: Test Files & Documentation ⏱️ 30 phút

**Status:** ⬜ Not Started

### Step 7.1: Move Test Files
- [ ] Create tests/processors/core/ directory
- [ ] Create tests/processors/technical/ directory
- [ ] Move PROCESSORS/core/shared/test_*.py (3 files)
- [ ] Move PROCESSORS/technical/commodity/test_commodity.py

### Step 7.2: Remove Doc Duplicates
- [ ] Delete docs/CLAUDE.md (keep root version)
- [ ] Delete docs/README.md (keep root version)

**Completion:** 0 / 6 tasks

---

## PHASE 8: Final Validation & Testing ⏱️ 1 giờ

**Status:** ⬜ Not Started

### Step 8.1: Test Calculators
- [ ] Run fundamental/calculators/company_calculator.py
- [ ] Run fundamental/calculators/bank_calculator.py
- [ ] Run valuation/calculators/historical_pe_calculator.py
- [ ] Run valuation/calculators/vnindex_pe_calculator_optimized.py
- [ ] Run technical/daily_ohlcv_update.py

### Step 8.2: Test Streamlit App
- [ ] Run `streamlit run WEBAPP/main_app.py`
- [ ] Check all 7 pages load without errors
- [ ] Verify data displays with correct formatting
- [ ] Verify no import errors

### Step 8.3: Update Documentation
- [ ] Update CLAUDE.md with refactor summary
- [ ] Add "Recent Refactoring (2025-12-10)" section

**Completion:** 0 / 10 tasks

---

## 📈 METRICS DASHBOARD

### Files Impact
| Category | Before | After | Change |
|----------|--------|-------|--------|
| Total Files | 114 | 95 | -19 ✅ |
| Old Paths | 33 | 0 | -33 ✅ |
| Broken Imports | 3 | 0 | -3 ✅ |
| Vietnamese Docstrings | 19 | 49 | +30 ✅ |
| Backup Files | 13 | 0 | -13 ✅ |
| Empty Folders | 3 | 0 | -3 ✅ |
| SchemaRegistry Usage | 0% | 100% | +100% ✅ |

### Code Health
| Module | Before | After | Target |
|--------|--------|-------|--------|
| PROCESSORS/fundamental | 85% | ⬜ | 100% |
| PROCESSORS/technical | 65% | ⬜ | 95% |
| PROCESSORS/valuation | 50% | ⬜ | 100% |
| WEBAPP | 60% | ⬜ | 95% |
| **Overall** | 72% | ⬜ | **97%** |

---

## 📝 NOTES & ISSUES

### Completed Phases
_(Ghi chú khi hoàn thành mỗi phase)_

**Phase 1: PROCESSORS/valuation** ✅ (2025-12-10)
- Đã hoàn thành xóa 5 file trùng lặp trong folder core/
- Đã cập nhật import paths cho 6 file calculator
- Đã thêm Vietnamese docstrings cho 5 file
- Tổng thời gian thực hiện: ~45 phút
- Không có vấn đề phát sinh

**Phase 2: PROCESSORS/fundamental** ✅ (2025-12-10)
- Đã hoàn thành xóa 5 file trùng lặp trong folder base/
- Không tìm thấy imports từ fundamental.base cần cập nhật
- Đã thêm Vietnamese docstrings cho 4 calculator files
- Tổng thời gian thực hiện: ~30 phút
- Không có vấn đề phát sinh

**Phase 3: PROCESSORS/technical** ✅ (2025-12-10)
- Đã hoàn thành xóa folder archive/deprecated_v1.0/
- Đã cập nhật paths trong 8 files (data_warehouse → DATA, calculated_results → DATA/processed)
- Đã xóa try/except fallback imports trong 3 files
- Đã thêm Vietnamese docstrings cho 6 files chính
- Tổng thời gian thực hiện: ~50 phút
- Không có vấn đề phát sinh

**Phase 4: WEBAPP Namespace Fixes** ✅ (2025-12-10)
- Đã sửa tất cả imports từ `streamlit_app.*` → `WEBAPP.*` trong 3 files
- Các file import errors đã được khắc phục
- Tổng thời gian thực hiện: ~15 phút
- Không có vấn đề phát sinh

---

### Issues Encountered
_(Ghi lại các vấn đề phát sinh)_

---

### Deferred Tasks
_(Tasks bị hoãn lại để sau)_

---

**Last Updated:** 2025-12-10
**Status:** 🔄 In Progress | ⬜ Not Started | ✅ Completed
