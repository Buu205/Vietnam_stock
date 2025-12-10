# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES FOR AI ASSISTANTS

### Rule 1: Update Existing Documentation, Don't Create New Files

**ALWAYS update existing markdown files instead of creating new ones.**

When documenting:
- ✅ **DO**: Update existing `.md` files in `.cursor/plans/` or root directory
- ✅ **DO**: Append new sections to existing documentation
- ✅ **DO**: Use clear section headers (##, ###) for organization
- ❌ **DON'T**: Create new `.md` files unless explicitly requested
- ❌ **DON'T**: Duplicate information across multiple files
- ❌ **DON'T**: Create "part 1", "part 2" files - use sections instead

**Primary Documentation Locations:**
- `.cursor/plans/*.md` - Active development plans (update these!)
- `CLAUDE.md` - This file (project instructions)
- `README.md` - User-facing documentation
- `docs/archive/` - Historical documentation (read-only)

### Rule 2: Check for Existing Plans Before Creating

Before creating any documentation:
1. Search for existing plan files: `find .cursor/plans -name "*.md"`
2. If similar plan exists, update it
3. If creating new plan is necessary, consolidate related content first

---

## Project Overview

Vietnamese stock market financial data dashboard and analysis system.

**Primary development location:** `/Users/buuphan/Dev/Vietnam_dashboard`

**Current Status:**
- ✅ Phase 0 complete (registries, calculators, transformers, schemas) - 40%
- 🚨 Phase 0.5 **CRITICAL** - Path Migration needed (95% files using wrong paths)
- ⏳ Phase 1 pending - FA+TA Sector Analysis orchestration layer
- 📋 Active Plan: `.cursor/plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`

---

## 🚨 CRITICAL: v4.0.0 Path Migration Status

**BLOCKING ISSUE:** Only **4.7% (2/43 files)** follow canonical architecture!

### Canonical v4.0.0 Paths (TARGET)

\`\`\`
DATA/
├── raw/                    # Input data (READ from here)
└── processed/              # Output data (WRITE to here)
    ├── fundamental/
    ├── technical/
    ├── valuation/
    └── forecast/bsc/
\`\`\`

### Current (WRONG) Paths - Need Migration

❌ **35 files (81.4%)** still use old paths:
- `calculated_results/` → Should be `DATA/processed/`
- `data_warehouse/raw/` → Should be `DATA/raw/`
- `DATA/refined/` → Should be `DATA/processed/`

**See Section 1.5 in plan for complete migration strategy.**

---

## Active Development Plan

**Primary Plan:** `.cursor/plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`

**Current Phase:** Phase 0.5 - Path Migration (BLOCKING)

**See plan file for complete roadmap.**

---

## Documentation Rules (RECAP)

1. ✅ **UPDATE** existing `.md` files in `.cursor/plans/`
2. ✅ **APPEND** new sections to existing documentation
3. ✅ **CONSOLIDATE** related content into single files
4. ❌ **DON'T** create new `.md` files without checking existing ones
5. ❌ **DON'T** duplicate information across files

**When in doubt, update the active plan file.**
