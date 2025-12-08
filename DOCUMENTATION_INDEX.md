# 📚 DOCUMENTATION INDEX

**Vietnam Stock Dashboard - Complete Documentation Guide**
**Version:** v4.0.0 Canonical Architecture
**Last Updated:** 2025-12-08

---

## 🚀 START HERE

Nếu bạn mới bắt đầu hoặc cần tra cứu nhanh, đọc theo thứ tự này:

1. **QUICK_REFERENCE.md** ⭐ - Commands để chạy hàng ngày
2. **WORKFLOW_DIAGRAM.md** - Visual data flow diagram
3. **ARCHITECTURE_STANDARDS.md** - Quy chuẩn architecture đầy đủ
4. **This file** - Navigation guide

---

## 📖 DOCUMENTATION BY PURPOSE

### 💡 Tôi cần biết...

#### "...chạy lệnh gì khi cập nhật dữ liệu?"
→ **QUICK_REFERENCE.md** (3 minutes read)
- Quarterly fundamental update commands
- Daily valuation/technical update commands
- Common issues & solutions
- ⭐ BOOKMARK FILE NÀY!

#### "...data flow hoạt động như thế nào?"
→ **WORKFLOW_DIAGRAM.md** (5 minutes read)
- Complete data pipeline visualization
- 5-layer architecture diagram
- Entity-specific metric codes table
- Testing workflow
- Daily/quarterly schedule

#### "...quy chuẩn architecture đầy đủ?"
→ **ARCHITECTURE_STANDARDS.md** (15 minutes read)
- DATA folder structure (refined/ vs processed/)
- PROCESSOR architecture (5 layers)
- Entity-specific metric codes mapping
- Complete workflow commands
- Testing & validation procedures
- Update checklist

#### "...chi tiết từng file PROCESSORS làm gì?"
→ **DATA_FLOW_COMPLETE_MAPPING.md** (20 minutes read)
- Complete RAW → PROCESSOR → RESULT mapping
- All Python files detailed table (purpose, input, output)
- Formula extraction status
- Layer-by-layer breakdown
- Entity-specific processing

#### "...valuation formulas (PE/PB/EV) hoạt động ra sao?"
→ **VALUATION_FORMULAS_COMPLETE_REPORT.md** (10 minutes read)
- 40+ valuation formulas explained
- Metric mapper usage (entity-specific codes)
- Integration examples (before/after)
- Testing verification results
- How to use in production

#### "...formula extraction plan và status?"
→ **FORMULA_EXTRACTION_PLAN.md** (10 minutes read)
- Week-by-week extraction plan
- Formula separation strategy
- Entity-specific formulas roadmap

→ **FORMULA_EXTRACTION_SUMMARY_REPORT.md** (5 minutes read)
- Current status: 75% complete
- What's done (Bank, Company, Valuation)
- What's pending (Insurance, Security)
- Parquet comparison results

#### "...project overview và setup?"
→ **CLAUDE.md** (20 minutes read)
- Complete project overview
- Development setup (Python 3.13, dependencies)
- Architecture & data flow
- Code conventions
- Development roadmap

→ **CURRENT_STATUS.md** (5 minutes read)
- Current implementation status
- Completed phases
- Next steps

#### "...hướng dẫn tùy chỉnh formulas?"
→ **docs/HUONG_DAN_TUY_CHINH_FORMULAS.md**
- Vietnamese guide for formula customization
- How to add new metrics
- Formula patterns & best practices

---

## 📁 FILE STRUCTURE OVERVIEW

```
/Users/buuphan/Dev/Vietnam_dashboard/
│
├── 📋 QUICK REFERENCE (⭐ START HERE!)
│   ├── QUICK_REFERENCE.md                    ← Commands cheat sheet
│   ├── WORKFLOW_DIAGRAM.md                   ← Visual data flow
│   └── DOCUMENTATION_INDEX.md                ← This file
│
├── 📚 ARCHITECTURE & STANDARDS
│   ├── ARCHITECTURE_STANDARDS.md             ← Complete architecture guide
│   ├── DATA_FLOW_COMPLETE_MAPPING.md         ← Detailed processors mapping
│   ├── CLAUDE.md                             ← Project overview
│   └── CURRENT_STATUS.md                     ← Implementation status
│
├── 🔬 FORMULA EXTRACTION
│   ├── FORMULA_EXTRACTION_PLAN.md            ← Week-by-week plan
│   ├── FORMULA_EXTRACTION_SUMMARY_REPORT.md  ← Status summary
│   └── VALUATION_FORMULAS_COMPLETE_REPORT.md ← Valuation formulas guide
│
├── 📂 DATA/
│   ├── refined/          ← ❌ CŨ (Raw input, Dec 1)
│   ├── processed/        ← ✅ MỚI (Calculated output, Dec 4+)
│   └── metadata/         ← Registries & schemas
│
├── 🔧 PROCESSORS/
│   ├── fundamental/      ← Financial calculators & formulas
│   ├── valuation/        ← PE/PB/EV calculators & formulas
│   ├── technical/        ← OHLCV & technical indicators
│   ├── transformers/     ← Pure calculation functions
│   └── pipelines/        ← Unified execution orchestrators
│
├── 🌐 WEBAPP/
│   └── main_app.py       ← Streamlit dashboard entry point
│
└── 📖 docs/
    ├── HUONG_DAN_TUY_CHINH_FORMULAS.md  ← Formula customization guide
    ├── MASTER_PLAN.md                    ← Development roadmap
    └── TRANSFORMERS_LAYER_GUIDE.md       ← Transformers explained
```

---

## 🎯 DOCUMENTATION BY ROLE

### 👨‍💻 Developer (Adding new features)
Read in this order:
1. CLAUDE.md - Project setup & conventions
2. ARCHITECTURE_STANDARDS.md - Architecture patterns
3. DATA_FLOW_COMPLETE_MAPPING.md - Understand data flow
4. docs/TRANSFORMERS_LAYER_GUIDE.md - How to write formulas

### 📊 Data Analyst (Running updates)
Read in this order:
1. QUICK_REFERENCE.md - Daily/quarterly commands
2. WORKFLOW_DIAGRAM.md - Understand the pipeline
3. ARCHITECTURE_STANDARDS.md (Section 3 & 7) - Workflows & checklists

### 🏗️ Architect (Understanding system)
Read in this order:
1. ARCHITECTURE_STANDARDS.md - Complete architecture
2. DATA_FLOW_COMPLETE_MAPPING.md - Detailed mapping
3. CLAUDE.md - Project overview
4. docs/MASTER_PLAN.md - Future roadmap

---

## 📊 DOCUMENTATION METRICS

| File | Size | Lines | Purpose | Read Time |
|------|------|-------|---------|-----------|
| QUICK_REFERENCE.md | 5KB | 150 | Commands cheat sheet | 3 min |
| WORKFLOW_DIAGRAM.md | 10KB | 350 | Visual data flow | 5 min |
| ARCHITECTURE_STANDARDS.md | 15KB | 545 | Architecture guide | 15 min |
| DATA_FLOW_COMPLETE_MAPPING.md | 26KB | 850 | Processors mapping | 20 min |
| VALUATION_FORMULAS_COMPLETE_REPORT.md | 12KB | 394 | Valuation formulas | 10 min |
| FORMULA_EXTRACTION_PLAN.md | 20KB | 650 | Extraction plan | 10 min |
| CLAUDE.md | 35KB | 1,100 | Project overview | 20 min |

**Total:** ~133KB of documentation, ~1.5 hours to read everything

---

## 🔍 SEARCH BY KEYWORD

### "Calculator"
- ARCHITECTURE_STANDARDS.md → Section 2 (Processor Architecture)
- DATA_FLOW_COMPLETE_MAPPING.md → Section 6.1-6.4 (All calculators)
- QUICK_REFERENCE.md → Section 1 (Commands)

### "Formula"
- VALUATION_FORMULAS_COMPLETE_REPORT.md → Complete guide
- FORMULA_EXTRACTION_SUMMARY_REPORT.md → Status
- docs/HUONG_DAN_TUY_CHINH_FORMULAS.md → Customization
- docs/TRANSFORMERS_LAYER_GUIDE.md → Pure functions

### "Metric Code"
- VALUATION_FORMULAS_COMPLETE_REPORT.md → Section 3 (Metric Codes Mapping)
- ARCHITECTURE_STANDARDS.md → Section 5 (Entity-Specific Codes)
- WORKFLOW_DIAGRAM.md → Entity-Specific Metric Codes Table

### "Data Flow"
- WORKFLOW_DIAGRAM.md → Complete flow diagram
- DATA_FLOW_COMPLETE_MAPPING.md → Detailed mapping
- ARCHITECTURE_STANDARDS.md → Section 11 (Data Flow Diagram)

### "Update"
- QUICK_REFERENCE.md → Daily/quarterly update commands
- ARCHITECTURE_STANDARDS.md → Section 3 (Workflow)
- WORKFLOW_DIAGRAM.md → Section 2 (Workflow by Use Case)

### "Testing"
- ARCHITECTURE_STANDARDS.md → Section 6 (Testing Workflow)
- WORKFLOW_DIAGRAM.md → Testing Workflow diagram
- FORMULA_EXTRACTION_SUMMARY_REPORT.md → Test results

---

## ✅ QUICK CHECKLIST

### New to the project?
- [ ] Read QUICK_REFERENCE.md
- [ ] Read WORKFLOW_DIAGRAM.md
- [ ] Skim ARCHITECTURE_STANDARDS.md
- [ ] Try running a daily update command
- [ ] Read CLAUDE.md for full context

### Need to update data?
- [ ] Open QUICK_REFERENCE.md
- [ ] Find relevant section (Quarterly/Daily)
- [ ] Copy & paste commands
- [ ] Check output in DATA/processed/

### Adding new feature?
- [ ] Read ARCHITECTURE_STANDARDS.md
- [ ] Read DATA_FLOW_COMPLETE_MAPPING.md
- [ ] Review existing calculator patterns
- [ ] Follow 5-layer architecture
- [ ] Write tests

### Debugging issue?
- [ ] Check QUICK_REFERENCE.md → Common Issues
- [ ] Check ARCHITECTURE_STANDARDS.md → Section 8
- [ ] Review WORKFLOW_DIAGRAM.md → Error Handling
- [ ] Check logs in `/logs/processors/`

---

## 🔄 DOCUMENTATION MAINTENANCE

**Last Major Update:** 2025-12-08 (v4.0.0 Release)

**Update Frequency:**
- QUICK_REFERENCE.md - Update monthly or when commands change
- ARCHITECTURE_STANDARDS.md - Update with each major version
- CURRENT_STATUS.md - Update after each phase completion
- Other docs - Update as needed

**Contribution Guidelines:**
- Keep QUICK_REFERENCE.md under 200 lines (readability)
- Include code examples in technical docs
- Use emojis for visual navigation
- Vietnamese translations for critical commands
- Update this index when adding new docs

---

## 📞 SUPPORT

**For questions about:**
- Architecture & design → Read ARCHITECTURE_STANDARDS.md
- Daily operations → Read QUICK_REFERENCE.md
- Data flow → Read WORKFLOW_DIAGRAM.md
- Formulas → Read VALUATION_FORMULAS_COMPLETE_REPORT.md

**Still stuck?**
- Check `/logs/processors/` for error logs
- Review ARCHITECTURE_STANDARDS.md → Section 8 (Common Issues)
- Check CLAUDE.md → Testing section

---

## 🎉 SUMMARY

**3 MOST IMPORTANT FILES:**
1. **QUICK_REFERENCE.md** - Your daily cheat sheet
2. **WORKFLOW_DIAGRAM.md** - Understand the flow
3. **ARCHITECTURE_STANDARDS.md** - Complete guide

**Everything else** provides deeper context and details.

**📌 TIP:** Bookmark QUICK_REFERENCE.md for instant access to commands!

---

**Generated by:** Claude Code
**Version:** 1.0
**Date:** 2025-12-08
**Status:** ✅ Complete Documentation Suite
