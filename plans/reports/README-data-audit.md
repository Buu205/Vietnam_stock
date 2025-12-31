# DATA REGISTRY AUDIT - Report Index

**Audit Date:** 2025-12-31  
**Scope:** Complete DATA directory vs. data_mapping registry  
**Status:** ⚠️ CRITICAL - 74% of files unregistered

---

## Quick Start

**Start here:**
1. Read: [`scout-20251231-summary.txt`](./scout-20251231-summary.txt) (2 min - critical findings)
2. Decide: Use action items to prioritize work
3. Reference: Use CSV for file list

---

## Reports Generated

### 📊 Audit Reports (Detailed Analysis)

| Report | Size | Purpose | Key Finding |
|--------|------|---------|------------|
| **[scout-20251231-data-audit.md](./scout-20251231-data-audit.md)** | 351 lines | Full audit with all details | 40 orphaned files, 3 duplicate sets |
| **[scout-20251231-summary.txt](./scout-20251231-summary.txt)** | 264 lines | Executive summary (start here) | 14/54 registered (26% coverage) |

### 📋 Reference Materials

| Document | Format | Contents |
|----------|--------|----------|
| **[scout-20251231-orphaned-files-quick-ref.csv](./scout-20251231-orphaned-files-quick-ref.csv)** | CSV | All 40 orphaned files with priority/action |

---

## Critical Findings at a Glance

```
OVERALL: Registry is 26% complete

Category        | Registered | Orphaned | Coverage
                |-----------|----------|----------
Fundamental     |     4     |    5     |   44%
Valuation       |     4     |    4     |   50%
Technical       |     2     |   22     |    8% ⚠️
Macro           |     1     |    5     |   17% ⚠️
Sector          |     1     |    1     |   50%
Forecast        |     2     |    2     |   50%
Raw             |     1     |    4     |   20% ⚠️
────────────────|-----------|----------|──────────
TOTAL           |    14     |   40     |   26% ⚠️
```

---

## Orphaned Files by Priority

### 🔴 CRITICAL (5 files - DELETE or REGISTER TODAY)

1. **DELETE:** `ev_ebitda_historical_test.parquet`
   - Location: `DATA/processed/valuation/ev_ebitda/historical/`
   - Reason: Orphaned test file, no longer needed

2. **REGISTER:** `historical_ps.parquet` as `ps_historical`
   - Location: `DATA/processed/valuation/ps/historical/`
   - Purpose: Price/Sales ratio valuation metric

3. **REGISTER:** `sector_fundamental_metrics.parquet`
   - Location: `DATA/processed/sector/`
   - Purpose: Complements sector_valuation (registered)

4. **REGISTER/CONSOLIDATE:** 4 macro indicators
   - Location: `DATA/processed/fundamental/macro/`
   - Files: `{deposit,exchange,gov_bond,interest}_rates.parquet`
   - Decision: Keep separate or consolidate into macro_commodity?

### 🟠 HIGH PRIORITY (26 files - REGISTER THIS WEEK)

**Technical Alerts (10 files):**
- 5x daily snapshots (breakout, pattern, volume, MA, combined)
- 5x historical records (same categories)

**Money Flow Analysis (5 files):**
- Individual money flow
- Sector money flow (3 timeframes: 1d, 1w, 1m)

**Market Indicators (5 files):**
- Market regime history
- Relative strength rating
- Sector breadth
- VN-Index indicators
- VCI coverage universe

**Individual Valuation Multiples (3 files):**
- Individual PE (potential duplicate?)
- Individual PB (potential duplicate?)
- Individual EV/EBITDA

### 🟡 MEDIUM PRIORITY (5 files - AUDIT & DECIDE)

**"Full" Data Copies (4 files) - Unclear Purpose:**
- `bank_full.parquet`
- `company_full.parquet`
- `insurance_full.parquet`
- `security_full.parquet`

**Action:** Clarify if these are working copies, backups, or legacy. Can they be removed?

**BSC Combined (1 file):**
- `bsc_combined.parquet`
- Action: Is this actively used? Register or remove?

### 🟢 LOW PRIORITY (4 files - CONSOLIDATE)

**News Raw Data (4 dated snapshots):**
- Implement versioning or rolling window
- Keep only latest snapshot

---

## Duplicates to Investigate

### Set #1: Individual vs. Historical PE Ratios
```
Registered:   valuation/pe/historical/historical_pe.parquet
Orphaned:     stock_valuation/individual_pe.parquet
Question:     Are these identical or truly different?
```

### Set #2: Individual vs. Historical PB Ratios
```
Registered:   valuation/pb/historical/historical_pb.parquet
Orphaned:     stock_valuation/individual_pb.parquet
Question:     Consolidate if identical?
```

### Set #3: "Full" vs. "Metrics" Entity Data
```
Registered:   fundamental/{entity}/financial_metrics.parquet
Orphaned:     fundamental/{entity}_full.parquet
Question:     Are "*_full" working copies? Legacy? Can be removed?
```

### Set #4: Macro Unified vs. Individual
```
Registered:   macro_commodity_unified.parquet (1 file)
Orphaned:     4 separate economic indicators
Question:     Should be 1 or 4 sources?
```

---

## Directory Size Summary

| Directory | Size | Files | % Registered | Notes |
|-----------|------|-------|------------|-------|
| fundamental/ | 116 MB | 9 | 44% | Includes 4 "*_full" copies |
| valuation/ | 46 MB | 8 | 50% | Includes duplicates |
| stock_valuation/ | 32 MB | 3 | 0% | Potential duplicates |
| technical/ | 27 MB | 24 | 8% | Severely underregistered ⚠️ |
| sector/ | 7.3 MB | 2 | 50% | Only 1 of 2 registered |
| macro_commodity/ | 400 KB | 1 | 100% | Only unified macro |
| forecast/ | 312 KB | 4 | 50% | BSC + VCI |
| market_indices/ | 0 B | 0 | — | Empty directory |
| **TOTAL** | **~230 MB** | **54** | **26%** | **~37 MB potential waste** |

---

## Action Plan

### Today (1-2 hours)
- [ ] Delete test file: `ev_ebitda_historical_test.parquet`
- [ ] Review "*_full.parquet" files in code
- [ ] Decide macro strategy (unified vs. separate)

### This Week (2-3 hours)
- [ ] Add 11 critical sources to `data_sources.yaml`
- [ ] Update `dashboards.yaml` with technical sources
- [ ] Create `DATA/README.md` documenting structure

### This Month (4-6 hours)
- [ ] Complete technical registry (all 22 files)
- [ ] Audit & consolidate duplicates
- [ ] Map pipelines to outputs (documentation)
- [ ] Establish data governance policy

---

## Questions for Review

1. **"*_full.parquet" files:** Working copies, backups, or legacy? Can they be removed?
2. **Individual multiples:** Are `stock_valuation/individual_*` true duplicates? Consolidate?
3. **Macro strategy:** Unified or separate registrations for economic indicators?
4. **Technical files:** Which dashboards/services use the 22 orphaned technical files?
5. **VCI & BSC:** Are forecast/VCI and bsc_combined actively used?
6. **News data:** Keep all 4 snapshots or implement versioning?

---

## Files in This Report Set

```
scout-20251231-data-audit.md
├── Executive summary
├── 10 sections (Part 1-7)
├── Orphaned files grouped by type
├── Duplicate analysis
├── Recommendations
└── Complete file inventory

scout-20251231-summary.txt
├── Critical findings
├── Priority breakdowns (critical/high/medium/low)
├── Registry entries (14 files)
├── Duplicate analysis
├── Recommendations & immediate actions
├── Directory size analysis
└── Questions for stakeholder

scout-20251231-orphaned-files-quick-ref.csv
└── All 40 orphaned files in CSV format
    ├── File path
    ├── Category
    ├── Priority
    ├── Action
    └── Notes
```

---

## How to Use These Reports

**For Quick Decisions:**
1. Open `scout-20251231-summary.txt`
2. Review action items
3. Use CSV for detailed file list

**For Implementation:**
1. Read full `scout-20251231-data-audit.md`
2. Open CSV and filter by priority
3. Reference duplicate sections for consolidation strategy

**For Documentation:**
1. Extract sections from audit report
2. Create DATA/README.md
3. Link from main README.md

---

## Recommendations Summary

### Must Do
- ✅ Delete test file
- ✅ Register ps_historical
- ✅ Register sector_fundamental_metrics
- ✅ Register/consolidate macro indicators

### Should Do
- 📋 Register all technical alert sources (or consolidate)
- 📋 Register money flow sources
- 📋 Register market indicator sources

### Nice to Have
- 📝 Audit & consolidate duplicates
- 📝 Establish data governance policy
- 📝 Complete pipeline documentation

---

**Report Version:** 1.0  
**Generated:** 2025-12-31  
**Next Review:** After critical registrations complete

See [`scout-20251231-summary.txt`](./scout-20251231-summary.txt) for actionable next steps.
