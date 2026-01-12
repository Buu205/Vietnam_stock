# Brainstorm: Docs Restructure

**Date:** 2026-01-04
**Goal:** Reorganize docs/ folder for better navigation and maintainability

---

## Current State Analysis

### Existing Files (9 total)
| File | Size | Category | Action |
|------|------|----------|--------|
| `TRADING_LOGIC.md` | 13KB | Logic | → `logic/technical.md` |
| `system-architecture.md` | 72KB | Architecture | → `architecture/system.md` |
| `webapp-architecture.md` | 11KB | Architecture | → `architecture/webapp.md` |
| `forecast-architecture.md` | 6KB | Architecture | → `architecture/forecast.md` |
| `codebase-summary.md` | 28KB | Reference | → `reference/codebase.md` |
| `code-standards.md` | 11KB | Reference | → `reference/standards.md` |
| `project-overview-pdr.md` | 10KB | Reference | → `reference/pdr.md` |
| `consensus-forecast-pipeline.md` | 9KB | Guide | → `guides/forecast-pipeline.md` |
| `archive/` | - | Historical | Keep as-is |

---

## Proposed Structure

```
docs/
├── README.md                     ← Index linking all docs
├── architecture/                 ← System design & data flow
│   ├── system.md                ← Full system architecture (72KB)
│   ├── webapp.md                ← WEBAPP structure
│   └── forecast.md              ← Forecast module design
├── logic/                        ← Pure business logic per page
│   ├── technical.md             ← Trading signals, thresholds (exists)
│   ├── bank.md                  ← Bank metrics logic (NEW)
│   ├── company.md               ← Company metrics logic (NEW)
│   ├── sector.md                ← Sector analysis logic (NEW)
│   ├── security.md              ← Security/brokerage logic (NEW)
│   ├── forecast.md              ← Forecast comparison logic (NEW)
│   └── fx-commodities.md        ← FX & commodity logic (NEW)
├── reference/                    ← Quick lookup docs
│   ├── codebase.md              ← Codebase summary
│   ├── standards.md             ← Code standards
│   └── pdr.md                   ← Product requirements
├── guides/                       ← How-to tutorials
│   └── forecast-pipeline.md     ← Consensus pipeline guide
└── archive/                      ← Historical docs (read-only)
```

---

## Logic Docs Template

Each page logic doc follows same structure:

```markdown
# {Page Name} Logic Reference

## Overview
- Purpose of this dashboard
- Key metrics displayed

## Section 1: {Tab/Component Name}
### Parameters
| Parameter | Value | File Location |
|-----------|-------|---------------|
### Logic Rules
- Rule 1
- Rule 2

## Section N: ...

## Global Parameters
| Parameter | Value | Description | File |
|-----------|-------|-------------|------|

## Color Reference
| State | Hex | Usage |
|-------|-----|-------|
```

---

## Pages Needing Logic Docs

| Page | Dashboard File | Priority | Complexity |
|------|----------------|----------|------------|
| Technical | `technical_dashboard.py` | ✅ Done | High (signals, rules) |
| Bank | `bank_dashboard.py` | 1 | Medium (NIM, NPL, CAR) |
| Company | `company_dashboard.py` | 2 | Medium (ROE, margins) |
| Sector | `sector_dashboard.py` | 3 | Medium (FA/TA scores) |
| Forecast | `forecast_dashboard.py` | 4 | Low (BSC vs consensus) |
| Security | `security_dashboard.py` | 5 | Low (broker metrics) |
| FX/Commodities | `fx_commodities_dashboard.py` | 6 | Low (price tracking) |

---

## Execution Plan

### Phase 1: Create Structure
1. Create folders: `architecture/`, `logic/`, `reference/`, `guides/`
2. Move existing files to appropriate folders
3. Rename files for consistency

### Phase 2: Create Logic Docs
4. Create `logic/bank.md` - Bank dashboard logic
5. Create `logic/company.md` - Company dashboard logic
6. Create `logic/sector.md` - Sector dashboard logic
7. Create remaining logic docs

### Phase 3: Link & Index
8. Create `docs/README.md` as navigation hub
9. Add cross-references between docs

---

## Decision: Proceed with Phase 1-3
