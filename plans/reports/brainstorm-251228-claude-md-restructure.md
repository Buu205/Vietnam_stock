# Brainstorm Report: CLAUDE.md Restructure (Approach 2 - Modular)

**Date:** 2025-12-28
**Decision:** Implement Approach 2 (Modular Rules System)
**Estimated Time:** 4-5 hours

---

## Problem Statement

Current CLAUDE.md (436 lines) has issues:
- Too long → Hard to navigate
- Mixed concerns → Temporary info (path migration) + permanent (conventions)
- No clear structure → AI reads everything linearly
- Hard to maintain → Update requires scrolling 436 lines
- No prioritization → All info equal weight

---

## Solution: Approach 2 - Modular Rules System

### Architecture

```
Vietnam_dashboard/
├── CLAUDE.md (100 lines)           # 🎯 Navigation hub + quick start
│
├── .claude/                        # 📋 AI-specific documentation
│   ├── rules/                      # Non-negotiable constraints
│   │   ├── critical.md            # Rule 1, Rule 2, path migration
│   │   ├── conventions.md         # Naming, code style, patterns
│   │   └── patterns.md            # Registry, paths, calculators
│   │
│   ├── guides/                     # Deep understanding
│   │   ├── architecture.md        # v4.0.0, registries, components
│   │   ├── data-flow.md           # Pipeline architecture
│   │   └── development.md         # Setup, environment, workflows
│   │
│   └── reference/                  # Lookup when needed
│       ├── commands.md            # All CLI commands
│       ├── paths.md               # Canonical v4.0.0 paths
│       └── formulas.md            # PE, PB, EV/EBITDA calculations
│
├── docs/                          # 📖 User-facing (keep as-is)
│   ├── project-overview-pdr.md
│   ├── system-architecture.md
│   ├── codebase-summary.md
│   └── code-standards.md
│
└── plans/                         # 📝 Active plans (keep as-is)
```

### Design Principles

1. **3-Tier Hierarchy:**
   - **Rules** (MUST READ) → Critical constraints
   - **Guides** (SHOULD READ) → Understanding system
   - **Reference** (AS NEEDED) → Lookup info

2. **Navigation Hub:**
   - CLAUDE.md = Entry point (~100 lines)
   - Points AI to right docs for each task

3. **Context-Aware:**
   - Fixing bug → Read rules + reference
   - Refactoring → Read guides + rules
   - New feature → Read all 3 tiers

---

## Migration Strategy

### Phase 1: Create Structure (30 min)

```bash
# Create directory structure
mkdir -p .claude/{rules,guides,reference}

# Create empty files
touch .claude/rules/{critical,conventions,patterns}.md
touch .claude/guides/{architecture,data-flow,development}.md
touch .claude/reference/{commands,paths,formulas}.md
```

### Phase 2: Extract Content (2-3 hours)

#### Content Mapping from CLAUDE.md (436 lines)

| Current Section | Lines | Target File | Rationale |
|----------------|-------|-------------|-----------|
| **Rule 1: Update Existing Docs** | ~30 | `.claude/rules/critical.md` | Non-negotiable constraint |
| **Rule 2: Check Existing Plans** | ~20 | `.claude/rules/critical.md` | Non-negotiable constraint |
| **Path Migration Status** | ~80 | `.claude/rules/critical.md` + `.claude/reference/paths.md` | Critical blocking issue |
| **Code Conventions** | ~50 | `.claude/rules/conventions.md` | Naming, style rules |
| **Registry Usage Patterns** | ~40 | `.claude/rules/patterns.md` | Technical patterns |
| **Calculator Patterns** | ~30 | `.claude/rules/patterns.md` | Don't duplicate |
| **v4.0.0 Architecture** | ~60 | `.claude/guides/architecture.md` | System design |
| **Registry System Deep Dive** | ~50 | `.claude/guides/architecture.md` | Part of architecture |
| **Data Flow** | ~40 | `.claude/guides/data-flow.md` | Pipeline flow |
| **Development Setup** | ~30 | `.claude/guides/development.md` | Environment, setup |
| **All Commands** | ~60 | `.claude/reference/commands.md` | CLI reference |
| **Canonical Paths** | ~40 | `.claude/reference/paths.md` | Path reference |
| **Valuation Formulas** | ~50 | `.claude/reference/formulas.md` | PE, PB, EV/EBITDA |

### Phase 3: Write New CLAUDE.md (1 hour)

New CLAUDE.md structure (~100 lines):

```markdown
# CLAUDE.md

## 🎯 Vai Trò & Persona
Senior Software Engineer - Financial Data Platforms
Focus: Clean code, Performance, Scalability (KISS)

## 📍 Project Context
Vietnamese stock market data platform:
- Domain: 457 tickers, 19 sectors, 4 entity types
- Features: Fundamental + Technical + Valuation + Forecast
- Tech: Python 3.13, Streamlit, Parquet, vnstock_data
- Status: Phase 0.5 (Path migration - CRITICAL)

## 🚨 CRITICAL RULES
**READ FIRST**: `.claude/rules/critical.md` before any code changes.

Top 3 Rules:
1. ALWAYS use registries (MetricRegistry, SectorRegistry)
2. ALWAYS use canonical paths (DATA/processed/, NOT calculated_results/)
3. NEVER duplicate calculators (use existing PROCESSORS/fundamental/calculators/)

## 📚 Documentation Structure

### Tầng 1: RULES (ĐỌC TRƯỚC)
- `.claude/rules/critical.md` - Non-negotiable constraints
- `.claude/rules/conventions.md` - Code style, naming
- `.claude/rules/patterns.md` - Registry, paths, calculators

### Tầng 2: GUIDES (HIỂU HỆ THỐNG)
- `.claude/guides/architecture.md` - v4.0.0 design, registries
- `.claude/guides/data-flow.md` - Pipeline architecture
- `.claude/guides/development.md` - Setup, environment

### Tầng 3: REFERENCE (TRA CỨU)
- `.claude/reference/commands.md` - All CLI commands
- `.claude/reference/paths.md` - Canonical v4.0.0 paths
- `.claude/reference/formulas.md` - PE, PB, EV/EBITDA

## 🚀 Quick Start
```bash
# Run dashboard
streamlit run WEBAPP/main_app.py

# Daily update
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Import registries
from config.registries import MetricRegistry, SectorRegistry
```

## ⚡ Workflow AI Nên Follow
1. Read `.claude/rules/critical.md`
2. Understand context from relevant guides
3. Follow conventions + patterns
4. Reference when needed
5. Check active plan progress

## 🔗 Important Links
- Active Plan: `.cursor/plans/fa+ta_sector_analysis_...md`
- Reports: `plans/reports/`
- User Docs: `docs/`
- Global Workflows: `~/.claude/workflows/`

## 📋 Current Priorities (UPDATED - Reality-Based)

**P0: Already Implemented ✅**
1. ✅ Path Resolution (100% compliance - no deprecated paths found)
2. ✅ Commit Messages (95% using Conventional Commits)
3. ✅ Logging Standards (85% compliance)

**P1: Standardization Needed ⚠️**
1. ⚠️ Docstring Google Style (45% → Target 80%)
2. ⚠️ Type Hints Universal (40% → Target 90%)
3. ⚠️ Registry Usage Expansion (23% → Target 70%)
4. ❌ Financial Validation (20% → Target 80%)

**P2: Design Standards (NEW) 📐**
1. 📐 AI Agent Selection Rules
2. 📐 Chart Design Standards (Plotly)
3. 📐 Typography System
4. 📐 Color Palette

## 🗣️ Communication Rules
- Ngắn gọn: Straight to the point
- Tiếng Việt: Response, code comments English
- Tư duy: Summary solution before code
```

### Phase 4: Validation (30 min)

Test scenarios:
1. **Bug fix scenario** → AI reads rules + reference
2. **Refactor scenario** → AI reads guides + rules
3. **New feature scenario** → AI reads all 3 tiers
4. **Path migration** → AI finds critical.md blocking issue

---

## File Templates

### `.claude/rules/critical.md`

```markdown
# Critical Rules (Non-Negotiable)

## Rule 1: Update Existing Documentation
**ALWAYS update existing markdown files instead of creating new ones.**

[Content from current CLAUDE.md Rule 1...]

## Rule 2: Check for Existing Plans
[Content from current CLAUDE.md Rule 2...]

## Rule 3: Path Resolution (✅ COMPLETED)

**STATUS: ✅ EXCELLENT (100% compliance)**

### Audit Results (2025-12-28):
- ✅ ZERO files using deprecated paths
- ✅ ALL files use `DATA/processed/`, `DATA/raw/`
- ✅ Path migration COMPLETED

### Current Standard (v4.0.0):
```python
# ✅ CORRECT - Manual construction
self.data_path = data_root / "DATA" / "processed" / "fundamental" / "company"

# ✅ BETTER - Centralized helper (recommended)
from PROCESSORS.core.config.paths import get_data_path
data_path = get_data_path("processed", "fundamental", "company")
```

### Deprecated Paths (NO LONGER USED):
- ❌ `calculated_results/` - REMOVED
- ❌ `data_warehouse/raw/` - REMOVED
- ❌ `DATA/refined/` - REMOVED

**Action:** Document current paths as standard
```

### `.claude/rules/conventions.md`

```markdown
# Code Conventions

## Naming Rules
- Files/modules: `snake_case`
- Classes: `CamelCase`
- Functions/variables: `snake_case`
- DataFrames: descriptive + `_df` suffix

## Path Resolution
[Extract from current CLAUDE.md...]

## Import Standards
[Extract from current CLAUDE.md...]
```

### `.claude/rules/patterns.md`

```markdown
# Technical Patterns (MUST FOLLOW)

## Pattern 1: ALWAYS Use Registries
```python
from config.registries import MetricRegistry, SectorRegistry

# Metric lookup
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")

# Sector lookup
sector_reg = SectorRegistry()
peers = sector_reg.get_peers("ACB")
```

## Pattern 2: Use Existing Calculators
[Extract from current CLAUDE.md...]

## Pattern 3: Transformer Functions
[Extract from current CLAUDE.md...]
```

### `.claude/guides/architecture.md`

```markdown
# v4.0.0 Architecture Guide

## Overview
[Extract "Architecture & Data Flow" from current CLAUDE.md...]

## Registry System
[Extract "Configuration & Registry System" from current CLAUDE.md...]

## Component Overview
[Extract completed/missing components tables...]
```

### `.claude/guides/data-flow.md`

```markdown
# Data Flow Architecture

## Pipeline Overview
[Extract data processing flow...]

## Input → Processing → Output
[Extract transformation flow...]
```

### `.claude/guides/development.md`

```markdown
# Development Guide

## Environment Setup
[Extract "Development Setup" from current CLAUDE.md...]

## Running the Project
[Extract commands...]

## Development Workflow
[Extract workflow steps...]
```

### `.claude/reference/commands.md`

```markdown
# Command Reference

## Daily Updates
```bash
# Unified daily update
python3 PROCESSORS/daily_sector_complete_update.py
```

## Fundamental Processing
[Extract all fundamental commands...]

## Registry Tools
[Extract registry builder commands...]
```

### `.claude/reference/paths.md`

```markdown
# Canonical v4.0.0 Paths

## Directory Structure
```
DATA/
├── raw/                # Input data
│   ├── ohlcv/
│   ├── fundamental/csv/
│   └── ...
│
└── processed/          # Output data
    ├── fundamental/
    ├── technical/
    └── valuation/
```

## Path Resolution Examples
[Extract path examples...]
```

### `.claude/reference/formulas.md`

```markdown
# Valuation Formulas Reference

## PE Ratio Calculation
[Extract from "Valuation Calculation Formulas" section...]

## PB Ratio
[Extract...]

## EV/EBITDA
[Extract...]
```

---

## Implementation Checklist

### Phase 1: Structure ✅
- [ ] Create `.claude/` directory
- [ ] Create `rules/`, `guides/`, `reference/` subdirectories
- [ ] Create 9 empty markdown files

### Phase 2: Content Migration ✅
- [ ] Extract critical rules → `.claude/rules/critical.md`
- [ ] Extract conventions → `.claude/rules/conventions.md`
- [ ] Extract patterns → `.claude/rules/patterns.md`
- [ ] Extract architecture → `.claude/guides/architecture.md`
- [ ] Extract data flow → `.claude/guides/data-flow.md`
- [ ] Extract development → `.claude/guides/development.md`
- [ ] Extract commands → `.claude/reference/commands.md`
- [ ] Extract paths → `.claude/reference/paths.md`
- [ ] Extract formulas → `.claude/reference/formulas.md`

### Phase 3: New CLAUDE.md ✅
- [ ] Write navigation hub (~100 lines)
- [ ] Add project context
- [ ] Add quick start
- [ ] Add documentation map
- [ ] Add workflow guide

### Phase 4: Validation ✅
- [ ] Test bug fix scenario
- [ ] Test refactor scenario
- [ ] Test new feature scenario
- [ ] Verify all links work
- [ ] Check AI understands structure

### Phase 5: Cleanup ✅
- [ ] Backup old CLAUDE.md → `.archive/CLAUDE.md.backup`
- [ ] Replace with new CLAUDE.md
- [ ] Commit changes

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| CLAUDE.md size | 436 lines | ~100 lines | ✅ |
| Navigation clarity | Low | High | ✅ |
| Update effort | High (scroll 436) | Low (edit specific file) | ✅ |
| AI parsing | Linear (all) | Selective (context-aware) | ✅ |
| Maintainability | Hard | Easy | ✅ |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Too many files** | Only 9 files total (manageable) |
| **AI confused** | Clear navigation in CLAUDE.md |
| **Broken links** | Validation phase checks all links |
| **Lost content** | Backup old CLAUDE.md first |
| **Time overrun** | Phases can be done incrementally |

---

## Next Steps

1. **User approval** of this migration plan
2. **Phase 1**: Create structure (30 min)
3. **Phase 2**: Extract content (2-3 hours)
4. **Phase 3**: Write new CLAUDE.md (1 hour)
5. **Phase 4**: Validate (30 min)
6. **Phase 5**: Cleanup & commit

---

## Unresolved Questions

1. Content language preference? (Vietnamese vs English for .claude/ files)
2. Keep old CLAUDE.md as backup? (symlink or delete)
3. Start implementation now or review plan first?
