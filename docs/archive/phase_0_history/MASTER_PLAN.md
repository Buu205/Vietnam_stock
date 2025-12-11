# 🎯 MASTER PLAN - Stock Dashboard Data Standardization

**TL;DR:** Đọc file này TRƯỚC, sau đó follow từng phase. Tất cả docs khác chỉ là reference.

**Last Updated:** 2025-12-07
**Current Phase:** ✅ Phase 0.1.6 COMPLETED | ➡️ Ready for Phase 2

---

## 📍 BẠN ĐANG Ở ĐÂU?

### ✅ HOÀN THÀNH (Đã xong, không cần làm lại)

#### Phase 0.1: Metric Registry ✅
- **File:** `metric_registry.json` (752 KB)
- **Lookup:** `data_processor/core/metric_lookup.py`
- **Tests:** 7/7 passed
- **Kết quả:** 2,099 metrics from BSC Excel → AI-readable JSON

#### Phase 0.1.5: Sector/Industry Mapping ✅
- **File:** `sector_industry_registry.json` (94.5 KB)
- **Lookup:** `data_processor/core/sector_lookup.py`
- **Integration:** `data_processor/core/unified_mapper.py` ⭐ **MAIN COMPONENT**
- **Tests:** 6/6 passed
- **Kết quả:** 457 tickers × 19 sectors × 4 entity types

#### Phase 0.1.6: OHLCV Data Standardization ✅
- **Files:** 
  - `ohlcv_data_schema.json` (OHLCV data schema)
  - `data_warehouse_schema.json` (Warehouse structure schema)
- **Key Features:** 
  - Display formatting rules for prices, volumes, percentages
  - Frequency codes (D, W, M, Q, Y) with clear descriptions
  - Validation rules for data quality
- **Integration:** Linked with fundamental and technical schemas
- **Kết quả:** Complete standardization for trading data from APIs

---

## 🎯 PHASE TIẾP THEO - CHỌN 1 TRONG 3 OPTIONS

### Option A: Solo Developer (Khuyến nghị) 👤
**Thời gian:** 4-6 tuần
**Chi phí:** $28.50/tháng (self-host)

```
✅ Phase 0.1   - Metric Registry (DONE)
✅ Phase 0.1.5 - Sector Mapping (DONE)
➡️ Phase 0.2   - Unified Calculators (2 tuần)
➡️ Phase 0.3   - Validation System (1 tuần)
⏭️ Phase 0.4   - DuckDB (optional, defer)
⏭️ Phase 0.5   - Automation (optional, defer)
```

**Bắt đầu:** Đọc `/docs/architecture/DATA_STANDARDIZATION.md` → Phase 0.2

---

### Option B: Full Data Standardization 📊
**Thời gian:** 3-4 tuần
**Chi phí:** $0 (chỉ dùng local tools)

```
✅ Phase 0.1   - Metric Registry (DONE)
✅ Phase 0.1.5 - Sector Mapping (DONE)
➡️ Phase 0.2   - Unified Calculators (2 tuần)
➡️ Phase 0.3   - Validation System (1 tuần)
➡️ Phase 0.4   - DuckDB Storage (3-4 ngày)
➡️ Phase 0.5   - Quarterly Automation (2-3 ngày)
```

**Bắt đầu:** Đọc `/docs/architecture/DATA_STANDARDIZATION.md` từ đầu

---

### Option C: Full Enhancement (Team/Commercial) 🚀
**Thời gian:** 10-12 tuần
**Chi phí:** $80-150/tháng

```
✅ Phase 0.1-0.1.5 - Foundation (DONE)
➡️ Phase 0.2-0.5   - Data Standardization (3 tuần)
➡️ Phase 1         - vnstock_ta migration (2 tuần)
➡️ Phase 2         - Real-time Alerts (2 tuần)
➡️ Phase 3         - MCP Servers (3 tuần)
➡️ Phase 4-6       - Database + AI + Web (5 tuần)
```

**Bắt đầu:** Đọc `/docs/architecture/FINAL_ANALYSIS.md` → Decision matrix

---

## 📚 FILE STRUCTURE - BIẾT ĐỌC FILE NÀO

### 🔴 CORE FILES - ĐỌC TRƯỚC

1. **`/docs/MASTER_PLAN.md`** ⭐ **ĐỌC FILE NÀY TRƯỚC!**
   - Overview toàn bộ kế hoạch
   - Chọn option phù hợp
   - Roadmap rõ ràng

2. **`/docs/architecture/DATA_STANDARDIZATION.md`** 🔴 **CRITICAL**
   - Chi tiết Phase 0.2-0.5
   - Implementation guide
   - Code examples

3. **`/docs/PHASE1_COMPLETION_REPORT.md`**
   - Summary Phase 0.1 (metric registry)
   - Test results
   - What's next

---

### 🟡 REFERENCE FILES - ĐỌC KHI CẦN

4. **`/docs/architecture/MAPPING_INTEGRATION_PLAN.md`**
   - Chi tiết Phase 0.1.5 implementation
   - UnifiedTickerMapper usage
   - Integration examples

5. **`/docs/architecture/SECTOR_INDUSTRY_MAPPING.md`**
   - Specification cho sector registry
   - Data structure
   - Validation requirements

6. **`/docs/ARCHITECTURE_SUMMARY.md`**
   - High-level overview
   - 6-phase enhancement plan
   - Cost & ROI summary

---

### 🟢 ADVANCED - CHỈ ĐỌC NẾU LÀM FULL ENHANCEMENT

7. **`/docs/architecture/ENHANCED_ROADMAP.md`** (Phase 1-2)
8. **`/docs/architecture/ENHANCED_ROADMAP_PART2.md`** (Phase 3-4)
9. **`/docs/architecture/ENHANCED_ROADMAP_PART3.md`** (Phase 5-6)
10. **`/docs/architecture/FINAL_ANALYSIS.md`** (ROI, costs, decision matrix)
11. **`/docs/architecture/ARCHITECTURE_ANALYSIS.md`** (Deep dive current state)

---

### ⚪ OBSOLETE - KHÔNG CẦN ĐỌC

- `/docs/architecture/README.md` → Thay bằng MASTER_PLAN.md này
- Các file trong `/docs/mongodb_mcp/` → Chỉ đọc nếu setup MongoDB

---

## 🗂️ DATA FILES STATUS

### ✅ ACTIVE - ĐANG SỬ DỤNG

```
data_warehouse/metadata/
├── metric_registry.json              ✅ Phase 0.1 output (KEEP)
├── sector_industry_registry.json     ✅ Phase 0.1.5 output (KEEP)
└── data_warehouse_schema.json        ✅ Phase 0.1.6 output (KEEP)

calculated_results/schemas/
├── fundamental_calculated_schema.json ✅ Existing schema (KEEP)
├── technical_calculated_schema.json   ✅ Existing schema (KEEP)
└── ohlcv_data_schema.json           ✅ Phase 0.1.6 output (KEEP)
```

### 📦 SOURCE - GIỮ LẠI ĐỂ REBUILD

```
data_warehouse/raw/metadata/
├── ticker_details.json               📦 Source for sector registry (KEEP)
├── entity_statistics.json            📦 Source for sector registry (KEEP)
└── ticker_entity_mapping.json        📦 Backup/legacy (KEEP for safety)
```

**Lý do giữ:** Nếu cần rebuild `sector_industry_registry.json`, chạy:
```bash
python3 data_processor/core/build_sector_registry.py
```

### 🗑️ CÓ THỂ XÓA (nếu muốn)

```
data_warehouse/raw/metadata/
└── all_tickers.csv                   🗑️ Optional (có thể xóa)
```

---

## 🛠️ CODE FILES STATUS

### ✅ ACTIVE - CORE COMPONENTS

```
data_processor/core/
├── metric_lookup.py                  ✅ Metric registry lookup
├── sector_lookup.py                  ✅ Sector registry lookup
├── unified_mapper.py                 ✅ ⭐ MAIN INTEGRATION
├── build_metric_registry.py          ✅ Build metric registry
├── build_sector_registry.py          ✅ Build sector registry
└── test_unified_mapper.py            ✅ Integration tests
```

### 📝 TODO - PHASE 0.2

```
data_processor/fundamental/base/
└── base_financial_calculator.py      ➡️ Create in Phase 0.2

data_processor/fundamental/{entity}/
├── {entity}_financial_calculator_v2.py   ➡️ Refactor in Phase 0.2
└── (entity = company, bank, insurance, security)
```

---

## 🚀 QUICK START - BẮT ĐẦU TỪ ĐÂY

### Nếu bạn muốn: "Làm tiếp Phase 0.2 - Unified Calculators"

```bash
# 1. Đọc plan
cat /Users/buuphan/Dev/stock_dashboard/docs/architecture/DATA_STANDARDIZATION.md

# 2. Tìm section "Phase 0.2"

# 3. Follow implementation plan từng bước

# 4. Test với unified_mapper
python3 data_processor/core/test_unified_mapper.py
```

---

### Nếu bạn muốn: "Tôi muốn xem tổng quan toàn bộ hệ thống"

```bash
# Đọc architecture summary
cat /Users/buuphan/Dev/stock_dashboard/docs/ARCHITECTURE_SUMMARY.md
```

---

### Nếu bạn muốn: "Tôi cần quyết định có làm full enhancement không"

```bash
# Đọc analysis với ROI, costs
cat /Users/buuphan/Dev/stock_dashboard/docs/architecture/FINAL_ANALYSIS.md

# Tìm section "Final Recommendations"
```

---

## 📊 CURRENT STATE SUMMARY

### ✅ What You Have Now

```
✓ 2,099 metrics mapped to Vietnamese names
✓ 457 tickers classified by sector + entity type
✓ UnifiedTickerMapper ready for use
✓ Auto-select calculator by ticker
✓ Validate metrics for entity types
✓ Search peers by sector
✓ Natural language query support
✓ OHLCV data standardized with display formats
✓ Data warehouse structure documented
✓ Integration between fundamental, technical, and trading data
```

### ➡️ What's Next (Phase 0.2)

```
→ Create BaseFinancialCalculator
→ Refactor 4 entity calculators
→ Reduce 60% code duplication
→ Use UnifiedTickerMapper for auto-selection
→ Easy to add new calculated metrics
```

**Estimated time:** 2 weeks
**Difficulty:** Medium
**Impact:** High (foundation for all future work)

---

## 🎯 RECOMMENDED PATH

### Cho Solo Developer (Bạn):

1. ✅ **DONE:** Phase 0.1 + 0.1.5 (metric + sector mapping)
2. ➡️ **NEXT:** Phase 0.2 (unified calculators) - **BẮT ĐẦU TỪ ĐÂY**
3. ➡️ **THEN:** Phase 0.3 (validation system)
4. ⏸️ **PAUSE:** Đánh giá xem có cần Phase 0.4-0.5 không
5. 🎯 **DECISION POINT:** Làm full enhancement hay dừng lại

### Timeline Dự Kiến:

```
Week 1-2: Phase 0.2 (Unified Calculators)
Week 3:   Phase 0.3 (Validation)
Week 4:   Decision point - continue or pause
```

---

## ❓ FAQ - CÂU HỎI THƯỜNG GẶP

**Q: Tôi nên đọc file nào trước?**
A: Đọc file này (MASTER_PLAN.md), sau đó:
- Muốn làm tiếp → `/docs/architecture/DATA_STANDARDIZATION.md`
- Muốn hiểu tổng quan → `/docs/ARCHITECTURE_SUMMARY.md`
- Muốn quyết định scope → `/docs/architecture/FINAL_ANALYSIS.md`

**Q: File cũ (ticker_details.json) có thể xóa không?**
A: KHÔNG. Giữ lại làm source để rebuild sector_registry.json khi cần.

**Q: Phase 0.1.5 đã xong, giờ làm gì?**
A: Follow Option A - Làm Phase 0.2 (Unified Calculators). Chi tiết trong DATA_STANDARDIZATION.md

**Q: Tôi có bắt buộc phải làm hết 6 phases enhancement không?**
A: KHÔNG. Chỉ cần làm Phase 0.1-0.3 (data standardization) là đủ cho solo dev.

**Q: Chi phí thật sự là bao nhiêu?**
A:
- Phase 0.1-0.3 (data standardization): $0 (local only)
- Phase 1-3 (foundation + alerts + MCP): $28.50/tháng
- Full enhancement (all 6 phases): $80-150/tháng

**Q: Tôi quên mất đang làm đến đâu, check như thế nào?**
A: Xem section "📍 BẠN ĐANG Ở ĐÂU?" ở đầu file này.

---

## 📞 NEED HELP?

### Stuck on Phase 0.2?
→ Đọc `/docs/architecture/DATA_STANDARDIZATION.md` section "Phase 0.2"

### Want to understand UnifiedTickerMapper?
→ Đọc `/docs/architecture/MAPPING_INTEGRATION_PLAN.md`

### Need to decide full enhancement?
→ Đọc `/docs/architecture/FINAL_ANALYSIS.md`

### Lost in documentation?
→ Quay lại file này (MASTER_PLAN.md) và chọn option phù hợp

---

## ✅ CHECKLIST - PHASE 0.2 (NEXT STEP)

```
Phase 0.2: Unified Calculator Refactoring
═══════════════════════════════════════════

Prerequisites:
✅ Phase 0.1 complete (metric registry)
✅ Phase 0.1.5 complete (sector mapping + unified mapper)
✅ UnifiedTickerMapper tests passing (6/6)

Week 1: Base Calculator
□ Day 1-2: Create BaseFinancialCalculator class
□ Day 3-4: Refactor CompanyFinancialCalculator v2
□ Day 5: Test & compare with old version

Week 2: Other Calculators
□ Day 1: Refactor BankFinancialCalculator v2
□ Day 2: Refactor InsuranceFinancialCalculator v2
□ Day 3: Refactor SecurityFinancialCalculator v2
□ Day 4-5: Integration tests + validation

Expected Results:
□ 60% code reduction
□ All 4 calculators use same base
□ Easy to add new metrics
□ Tests passing for all entities
```

**Ready to start?**
→ Open `/docs/architecture/DATA_STANDARDIZATION.md` and find "Phase 0.2"

---

**Good luck! 🚀**

*Last updated: 2025-12-07*
*Next review: After Phase 0.2 completion*
