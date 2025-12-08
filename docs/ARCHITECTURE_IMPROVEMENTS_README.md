# 🏗️ CẢI TIẾN KIẾN TRÚC - HƯỚNG DẪN NHANH

> **Đánh giá:** Vietnam Dashboard đạt **70% canonical compliance**
> **Cần làm:** 5 cải tiến chiến thuật (4-5h) để đạt **100%**

---

## 📊 TÓM TẮT ĐÁNH GIÁ

### ✅ Điểm mạnh (70% canonical)
- ✅ **DATA/PROCESSORS separation** - Hoàn hảo
- ✅ **Package structure** - Professional Python project
- ✅ **Centralized paths** - No hardcoded paths
- ✅ **No duplication** - Clean codebase (v3.0)

### 🔴 Cần cải thiện (30% còn lại)
- 🟡 **Raw vs Refined** - Một số parquet còn trong raw/
- 🟡 **Schema location** - Rải rác 3 nơi
- 🟡 **Validation** - Thiếu input/output validators
- 🟡 **Pipelines** - Fundamental chưa có unified pipeline

---

## 🚀 QUICK START

### Option 1: Tự động (RECOMMENDED) - 15-30 phút

```bash
cd /Users/buuphan/Dev/Vietnam_dashboard

# 1. Backup
git tag v3.0-before-canonical
git checkout -b canonical-migration

# 2. Preview changes
python3 docs/scripts/migrate_to_canonical.py --dry-run

# 3. Apply changes
python3 docs/scripts/migrate_to_canonical.py --execute

# 4. Test
python3 -c "from PROCESSORS.core.registries.schema_registry import schema_registry"
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# 5. Commit
git add .
git commit -m "feat: Migrate to canonical structure (70% → 90%)"
```

**Kết quả:** 70% → 90% canonical compliance

---

### Option 2: Manual (4-5 giờ)

Xem chi tiết: `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md` → "QUICK START GUIDE"

---

## 📚 TÀI LIỆU CHI TIẾT

### 1. Đánh giá chi tiết
**File:** `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md`
**Nội dung:**
- Phân tích 9 tiêu chí canonical
- So sánh cấu trúc hiện tại vs chuẩn
- 5 fixes với code examples
- Migration roadmap 3 tuần

### 2. Canonical structure reference
**File:** `/docs/CANONICAL_STRUCTURE_AND_IMPROVEMENTS.md`
**Nội dung:**
- Cấu trúc chuẩn lý tưởng
- Data flow patterns
- Best practices
- Updated với đánh giá thực tế (v2.0)

### 3. Migration script
**File:** `/docs/scripts/migrate_to_canonical.py`
**Chức năng:**
- Tự động migrate toàn bộ cấu trúc
- Dry-run mode để preview
- Validation & error handling
- Migration report

---

## 🎯 ROADMAP

### Week 1: Critical Fixes (4-5h) 🔴
| Task | Effort | Impact |
|------|--------|--------|
| Tách Raw vs Refined | 2-3h | ⭐⭐⭐ |
| Consolidate schemas | 1-2h | ⭐⭐⭐ |
| Update paths.py | 30m | ⭐⭐ |
| Test imports | 30m | ⭐⭐ |

**Kết quả:** 70% → 90% canonical

---

### Week 2: Validation & Pipelines (10-12h) 🟡
| Task | Effort | Impact |
|------|--------|--------|
| Input validator | 3-4h | ⭐⭐⭐ |
| Output validator | 3-4h | ⭐⭐⭐ |
| Unified pipeline | 3-4h | ⭐⭐ |

**Kết quả:** 90% → 95% canonical

---

### Week 3-4: Extractors & Transformers (12-18h) 🟢
| Task | Effort | Impact |
|------|--------|--------|
| Extractors layer | 4-6h | ⭐⭐ |
| Transformers layer | 8-12h | ⭐⭐ |

**Kết quả:** 95% → 100% canonical

---

## 🔍 CHANGES OVERVIEW

### Migration sẽ thay đổi gì?

#### 1. Data Structure
```diff
DATA/
- ├── processed/                    # Old name
+ ├── refined/                      # New name (clearer)
  │   ├── fundamental/
+ │   │   ├── current/              # Latest quarter
+ │   │   └── archive/              # Historical
  │   ├── technical/
  │   └── valuation/
  │
  ├── raw/
  │   ├── fundamental/
- │   │   └── processed/            # Confusing location
+ │   │   └── csv/                  # Clear raw input
+ │   │       ├── Q3_2025/
+ │   │       └── Q4_2025/
```

#### 2. Schema Location
```diff
- DATA/schemas/                     # Old location 1
- PROCESSORS/core/schemas/          # Old location 2
+ config/schemas/                   # Single source of truth
    ├── data/
    ├── validation/
    └── display/
```

#### 3. New Components
```diff
PROCESSORS/
+ ├── extractors/                   # NEW: Data loading
+ │   ├── csv_loader.py
+ │   └── api_loader.py
+ │
+ ├── transformers/                 # NEW: Pure calculations
+ │   ├── financial/
+ │   └── technical/
+ │
+ ├── pipelines/                    # NEW: Orchestrators
+ │   ├── quarterly_report.py
+ │   └── daily_update.py
+ │
  ├── core/
+ │   ├── validators/               # NEW: Validation
+ │   │   ├── input_validator.py
+ │   │   └── output_validator.py
+ │   └── registries/               # NEW: Schema registry
+ │       └── schema_registry.py
```

---

## ✅ SUCCESS CRITERIA

### Data Quality
- [ ] No processed files in `DATA/raw/`
- [ ] No raw files in `DATA/refined/`
- [ ] Clear quarterly organization

### Code Quality
- [ ] Single schema location
- [ ] SchemaRegistry working
- [ ] All imports updated

### Architecture
- [ ] Extractors layer created
- [ ] Validators integrated
- [ ] Unified pipeline functional

---

## 🆘 TROUBLESHOOTING

### Issue: Migration script fails

```bash
# Check Python version
python3 --version  # Should be 3.13

# Check project location
pwd  # Should be /Users/buuphan/Dev/Vietnam_dashboard

# Run with verbose output
python3 docs/scripts/migrate_to_canonical.py --dry-run
```

### Issue: Imports fail after migration

```bash
# Update PYTHONPATH
export PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard:$PYTHONPATH

# Test import
python3 -c "from PROCESSORS.core.registries.schema_registry import schema_registry"
```

### Issue: WEBAPP can't find data

```bash
# Check paths.py updated
grep "refined" PROCESSORS/core/config/paths.py

# Update WEBAPP imports
find WEBAPP -name "*.py" -exec sed -i '' 's/processed/refined/g' {} \;
```

---

## 📞 NEXT ACTIONS

### Immediate (Hôm nay)
1. Đọc `/docs/ARCHITECTURE_EVALUATION_AND_FIXES.md`
2. Chạy migration script với `--dry-run`
3. Review preview changes

### This Week (Tuần này)
1. Execute migration script
2. Test all calculators
3. Update WEBAPP paths
4. Commit changes

1

---

## 📚 FILES CREATED

| File | Purpose | Size |
|------|---------|------|
| `ARCHITECTURE_EVALUATION_AND_FIXES.md` | Chi tiết đánh giá & fixes | 15KB |
| `scripts/migrate_to_canonical.py` | Migration script | 10KB |
| `CANONICAL_STRUCTURE_AND_IMPROVEMENTS.md` (updated) | Canonical reference | 12KB |
| `ARCHITECTURE_IMPROVEMENTS_README.md` (this file) | Quick reference | 5KB |

---

## 🎯 KẾT LUẬN

**Tình trạng:** ✅ Ready to migrate
**Effort:** 4-5 giờ (manual) hoặc 15-30 phút (script)
**Impact:** High - Loại bỏ technical debt, chuẩn hóa codebase
**Risk:** Low - Script có dry-run mode, backup recommended

**Recommendation:** Chạy migration script **tuần này** để đạt 90% canonical compliance.

---

**Ngày:** 2025-12-08
**Author:** Claude Code
**Status:** ✅ Documentation Complete - Ready for execution
