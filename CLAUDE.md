# CLAUDE.md

Project guidance for Claude Code AI assistants working with the Vietnam Dashboard codebase.

---

## 🎯 Project Context

**Vietnamese stock market data platform:**
- **Domain:** 457 tickers × 19 sectors × 4 entity types
- **Features:** Fundamental + Technical + Valuation + Forecast analysis
- **Tech Stack:** Python 3.13, Streamlit, Parquet, vnstock_data
- **Status:** v4.0.0 architecture (40% complete)

**Primary Location:** `/Users/buuphan/Dev/Vietnam_dashboard`

---

## 🚨 CRITICAL RULES (READ FIRST)

**Before making ANY code changes, read:** [`.claude/rules/critical.md`](.claude/rules/critical.md)

**Top 3 Non-Negotiable Rules:**
1. **ALWAYS use registries** (`MetricRegistry`, `SectorRegistry`, `SchemaRegistry`)
2. **ALWAYS use canonical paths** (`DATA/processed/`, `DATA/raw/` - NO deprecated paths)
3. **NEVER duplicate calculators** (use existing from `PROCESSORS/`)

**Path Migration Status:** ✅ Complete (100% compliance - all files use v4.0.0 paths)

---

## 📚 Documentation Structure

### Tier 1: RULES (READ BEFORE CODING)

**Non-negotiable constraints - MUST follow**

- [`.claude/rules/critical.md`](.claude/rules/critical.md) - Critical rules (registries, paths, calculators)
- [`.claude/rules/conventions.md`](.claude/rules/conventions.md) - Code style, naming, imports
- [`.claude/rules/patterns.md`](.claude/rules/patterns.md) - Technical patterns (registry usage, data loading, caching)

### Tier 2: GUIDES (UNDERSTAND SYSTEM)

**Deep understanding of architecture and data flow**

- [`.claude/guides/architecture.md`](.claude/guides/architecture.md) - v4.0.0 architecture, registries, components
- [`.claude/guides/data-flow.md`](.claude/guides/data-flow.md) - Pipeline architecture, data processing flow
- [`.claude/guides/development.md`](.claude/guides/development.md) - Setup, environment, development workflow

### Tier 3: REFERENCE (LOOKUP AS NEEDED)

**Quick reference for commands, paths, and formulas**

- [`.claude/reference/commands.md`](.claude/reference/commands.md) - All CLI commands (pipelines, calculators, dashboards)
- [`.claude/reference/paths.md`](.claude/reference/paths.md) - Canonical v4.0.0 paths (input/output locations)
- [`.claude/reference/formulas.md`](.claude/reference/formulas.md) - Valuation & financial formulas (PE, PB, ROE, etc.)

---

## 🚀 Quick Start

### Run Dashboard

```bash
streamlit run WEBAPP/main_app.py
# Opens at http://localhost:8501
```

### Daily Update

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
# ~45 minutes - updates all data
```

### Import Registries

```python
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry
from PROCESSORS.core.config.paths import get_data_path

# Single source of truth for all lookups
metric_reg = MetricRegistry()
sector_reg = SectorRegistry()
```

---

## ⚡ AI Workflow Guide

**When working on a task, follow this sequence:**

1. **Read critical rules** → [`.claude/rules/critical.md`](.claude/rules/critical.md)
2. **Understand context** → Relevant guides from [`.claude/guides/`](.claude/guides/)
3. **Follow patterns** → [`.claude/rules/patterns.md`](.claude/rules/patterns.md)
4. **Reference as needed** → [`.claude/reference/`](.claude/reference/) for commands/paths/formulas
5. **Check active plan** → See Current Priorities below

**Task-Specific Workflows:**

| Task Type | Read These Docs |
|-----------|----------------|
| **Bug fix** | Critical rules + Reference (paths/commands) |
| **Refactoring** | Critical rules + Architecture + Patterns |
| **New feature** | All 3 tiers (rules → guides → reference) |
| **Data pipeline** | Critical rules + Data Flow + Commands |
| **Dashboard UI** | Patterns + Development + Architecture |

---

## 📋 Current Priorities

**Active Plan:** `plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`

**Current Phase:** Phase 1 - FA/TA Orchestration Layer (Next Up)

**Next Steps:**
1. Build FA/TA orchestration layer (`SectorAnalyzer`, Aggregators, Combiner)
2. Configuration system (FA/TA weights, preferences)
3. Unified sector dashboard (Streamlit UI)

**See active plan for complete roadmap.**

---

## 🔗 Important Links

- **User Documentation:** [`docs/`](docs/) (project overview, architecture, code standards)
- **Reports:** [`plans/reports/`](plans/reports/) (audit reports, brainstorm sessions)
- **Global Workflows:** `~/.claude/workflows/` (primary workflow, development rules)

---

## 📝 Important Notes

- **No virtual environment** - Uses global Python 3.13
- **Data files expendable** - Files in `DATA/processed/` are generated artifacts
- **Single source of truth** - All lookups via registries
- **Parquet format** - All processed data stored as Parquet
- **Conventional commits** - Follow conventional commit format

---

## 🗣️ Communication Style

- **Concise:** Straight to the point
- **Vietnamese responses:** Code comments in English
- **Solution-first:** Summary before implementation

---

## Summary

**This file is your navigation hub.** Start here, then navigate to detailed docs:

1. 🚨 **Rules first** → [`.claude/rules/critical.md`](.claude/rules/critical.md)
2. 📖 **Understand system** → [`.claude/guides/`](.claude/guides/)
3. 📚 **Reference when needed** → [`.claude/reference/`](.claude/reference/)

**When in doubt:**
- Check critical rules first
- Read relevant guide for context
- Reference commands/paths/formulas as needed
- Follow active plan for priorities

**Happy coding! 🚀**
