# Brainstorm: Forecast Data Architecture Redesign

**Date:** 2026-01-04
**Type:** Hard Brainstorm
**Status:** Draft

---

## Problem Statement

Current forecast data is fragmented across multiple folders and files:
- 10 parquet files (228KB total)
- 3 JSON staging files (116KB)
- Raw PDF/screenshots scattered in `DATA/raw/concensus_report/`
- Multiple processing scripts with complex interdependencies

**User's Goal:** Simplify to 4 source JSONs → 1 unified parquet for Streamlit.

---

## Current State Analysis

### PROCESSORS/forecast Structure (After Restructure)
```
PROCESSORS/forecast/
├── bsc/                           # BSC Research Excel → parquet
│   ├── bsc_forecast_processor.py
│   └── bsc_update_script.py
├── vci/                           # VCI API → parquet
│   ├── vietcap_auth.py
│   ├── vietcap_client.py
│   ├── vci_update_script.py
│   └── integrate_vci_api.py
├── hcm_ssi_extraction/            # PDF/Screenshots → JSON → parquet
│   ├── pdf_extractor.py
│   ├── screenshot_extractor.py
│   └── hcm_ssi_update_script.py
├── comparison/
│   └── create_comparison_table.py
└── run_consensus_pipeline.py
```

### Current DATA Structure
```
DATA/raw/concensus_report/       # ← Typo in folder name
├── pdf/                         # 65MB PDFs
├── screenshots/
└── staging/                     # 3 JSON: hcm, ssi, vci raw extracts

DATA/processed/forecast/
├── VCI/                         # Case mismatch: VCI vs vci
│   ├── vci_coverage_universe.parquet (36KB)
│   └── vci_coverage_universe.json
├── bsc/
│   ├── bsc_individual.parquet (40KB)      ← Used by Tab 1,2,3
│   ├── bsc_sector_valuation.parquet (16KB) ← Used by Tab 2
│   └── bsc_combined.parquet (40KB)         ← For comparison
├── consensus/
│   ├── consensus_combined.parquet (12KB)
│   ├── consensus_summary.parquet (20KB)
│   ├── hcm_forecast.parquet (8KB)
│   ├── ssi_forecast.parquet (8KB)
│   └── vci_forecast.parquet (8KB)
└── comparison/
    └── bsc_vs_consensus.parquet (40KB)    ← Used by Tab 4
```

### WEBAPP Tab Data Dependencies
| Tab | Data Files Used |
|-----|-----------------|
| BSC Universal | `bsc_individual.parquet` |
| Sector | `bsc_sector_valuation.parquet` |
| Achievement | `bsc_individual.parquet` |
| Consensus | `bsc_vs_consensus.parquet` |

**Key Insight:** Streamlit only needs **3 parquet files**:
1. `bsc_individual.parquet` (stocks)
2. `bsc_sector_valuation.parquet` (sectors)
3. `bsc_vs_consensus.parquet` (comparison)

---

## Design Options

### Option A: Minimal Change (Keep Current + Cleanup)

Keep structure, just fix issues:
- Rename `concensus_report` → `consensus` (fix typo)
- Rename `VCI` → `vci` (lowercase consistency)
- Keep all parquet files (already small)

**Pros:** Low risk, minimal changes
**Cons:** Still fragmented, hard to understand

### Option B: User's Proposed Architecture (Recommended)

```
DATA/
├── raw/
│   └── forecast/
│       ├── bsc/
│       │   └── BSC_Forecast.xlsx           # Source Excel
│       └── hcm_ssi/                        # Moved from concensus_report
│           ├── pdf/                        # Strategy PDFs
│           ├── screenshots/                # Manual screenshots
│           └── staging/                    # Extracted JSONs
│
└── processed/
    └── forecast/
        ├── sources/                        # 4 source JSONs (editable)
        │   ├── bsc.json
        │   ├── vci.json
        │   ├── hcm.json
        │   └── ssi.json
        ├── bsc/                            # BSC-specific outputs
        │   ├── bsc_individual.parquet
        │   └── bsc_sector_valuation.parquet
        └── unified/                        # Single parquet for Streamlit
            └── forecast_unified.parquet    # All comparisons in one
```

**Architecture Flow:**
```
[BSC Excel] ─────────────────────────→ bsc.json ─┐
[VCI API] ───────────────────────────→ vci.json ─┤
[PDF/Screenshots] → [Gemini Extract] → hcm.json ─┼─→ forecast_unified.parquet
                                     → ssi.json ─┘
```

**Pros:**
- Single parquet load for Streamlit
- JSONs are human-editable for quick fixes
- Clear separation: raw → staging → processed
- Easy to add new sources (just add JSON)

**Cons:**
- Migration effort required
- Need to update all processors

### Option C: Hybrid (JSON Sources + Optimized Parquets)

Keep current parquet separation but add JSON staging layer:

```
DATA/processed/forecast/
├── staging/                    # 4 editable JSONs
│   ├── bsc.json
│   ├── vci.json
│   ├── hcm.json
│   └── ssi.json
├── bsc_individual.parquet      # For BSC tabs
├── bsc_sector.parquet          # For sector tab
└── comparison.parquet          # For consensus tab
```

**Pros:** Minimal WEBAPP changes
**Cons:** Still 3 parquets, slightly more complex than Option B

---

## Recommended: Option B with Modifications

### Final Proposed Structure

```
DATA/
├── raw/
│   └── forecast/
│       ├── bsc_excel/                      # BSC source
│       │   └── BSC_Forecast.xlsx
│       └── hcm_ssi/                        # HCM/SSI source
│           ├── pdf/
│           ├── screenshots/
│           └── extracted/                  # Raw JSON extracts
│               ├── hcm_raw.json
│               └── ssi_raw.json
│
└── processed/
    └── forecast/
        ├── sources/                        # ★ 4 NORMALIZED JSONs ★
        │   ├── bsc.json                    # (human-editable)
        │   ├── vci.json
        │   ├── hcm.json
        │   └── ssi.json
        │
        ├── bsc/                            # BSC-specific (for tabs 1-3)
        │   ├── individual.parquet
        │   └── sector.parquet
        │
        └── unified.parquet                 # ★ SINGLE FILE FOR COMPARISON ★
```

### JSON Schema (Normalized)

Each source JSON follows same schema for easy processing:

```json
{
  "source": "bsc",
  "updated_at": "2026-01-04T15:00:00",
  "schema_version": "2026F",
  "stocks": [
    {
      "symbol": "ACB",
      "sector": "Ngân hàng",
      "entity_type": "BANK",
      "target_price": 32000,
      "current_price": 26850,
      "rating": "BUY",
      "npatmi_2026f": 18500,
      "npatmi_2027f": 21000,
      "eps_2026f": 3200,
      "pe_2026f": 8.4,
      "notes": ""
    }
  ]
}
```

### Processing Pipeline

```
1. bsc_update_script.py    → sources/bsc.json
2. vci_update_script.py    → sources/vci.json  (via API)
3. hcm_ssi_update_script.py → sources/hcm.json, sources/ssi.json

4. build_unified.py        → unified.parquet (compare all sources)
5. build_bsc_outputs.py    → bsc/individual.parquet, bsc/sector.parquet
```

### Parquet Files for Streamlit (.gitignore exceptions)

```gitignore
# Forecast (3 files instead of 10)
!DATA/processed/forecast/bsc/individual.parquet
!DATA/processed/forecast/bsc/sector.parquet
!DATA/processed/forecast/unified.parquet
```

---

## Benefits Summary

| Metric | Before | After |
|--------|--------|-------|
| Parquet files | 10 | 3 |
| Total size | 228KB | ~100KB |
| Streamlit loads | 3-4 files | 1-3 files |
| Manual edit | Edit parquet (hard) | Edit JSON (easy) |
| Add new source | Complex pipeline | Add JSON file |
| Folder structure | Fragmented | Clean hierarchy |

---

## Migration Checklist

### Phase 1: Restructure Folders
- [ ] Create `DATA/raw/forecast/bsc_excel/`
- [ ] Create `DATA/raw/forecast/hcm_ssi/`
- [ ] Move `DATA/raw/concensus_report/*` → `DATA/raw/forecast/hcm_ssi/`
- [ ] Move `BSC Forecast.xlsx` → `DATA/raw/forecast/bsc_excel/`
- [ ] Delete old `DATA/raw/concensus_report/`

### Phase 2: Create JSON Source Layer
- [ ] Create `DATA/processed/forecast/sources/`
- [ ] Update `bsc_update_script.py` to output `sources/bsc.json`
- [ ] Update `vci_update_script.py` to output `sources/vci.json`
- [ ] Update `hcm_ssi_update_script.py` to output `sources/hcm.json`, `sources/ssi.json`

### Phase 3: Consolidate Parquets
- [ ] Create `build_unified.py` script
- [ ] Rename `bsc_individual.parquet` → `bsc/individual.parquet`
- [ ] Rename `bsc_sector_valuation.parquet` → `bsc/sector.parquet`
- [ ] Create `unified.parquet` from all sources
- [ ] Delete old `consensus/` and `comparison/` folders

### Phase 4: Update WEBAPP
- [ ] Update `ForecastService` paths
- [ ] Update `bsc_vs_consensus_tab.py` to use `unified.parquet`
- [ ] Test all 4 tabs

### Phase 5: Update .gitignore
- [ ] Remove old parquet exceptions
- [ ] Add new 3-file exceptions

---

## Open Questions

1. **VCI JSON:** Should we keep `vci.json` or use API directly each time?
   - Recommend: Keep JSON for offline fallback and manual edits

2. **BSC Excel location:** Move to `DATA/raw/` or keep in `DATA/processed/`?
   - Recommend: Move to `DATA/raw/forecast/bsc_excel/`

3. **Schema versioning:** How to handle 2025F→2026F→2027F year transitions?
   - Recommend: Use `schema_version` field in JSON, normalize in unified builder

4. **Folder naming:** Keep `hcm_ssi` or split `hcm/` and `ssi/`?
   - Recommend: Keep together as `hcm_ssi` since same extraction process

---

## Next Steps

1. User approval of Option B structure
2. Create detailed implementation plan
3. Implement Phase 1-5 in sequence
4. Test and validate

**Estimated Effort:** 2-3 hours
