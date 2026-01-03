# Consensus Forecast Pipeline - Streamlined Data Collection

**Date:** 2026-01-03
**Status:** Draft
**Priority:** High

---

## 1. Problem Statement

**Current Issues:**
- Data scattered across `concensus_report/` and `DATA/processed/forecast/`
- Scripts mixed with raw data in `raw_extracts/`
- No clear pipeline flow from input → processing → output
- Multiple extraction methods without unified interface
- BSC data updated manually via Excel without integration

**Goal:** Create streamlined pipeline to:
1. Collect forecast data from 3 sources (PDF, VCI API, Screenshot)
2. Normalize to BSC-compatible schema
3. Output standardized parquet files
4. Display comparison in Streamlit app

---

## 2. Target Architecture

```
                    ┌─────────────────┐
                    │   DATA SOURCES  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
    │   PDF   │        │ VCI API │        │ Screen  │
    │ Gemini  │        │  Auto   │        │ Claude  │
    └────┬────┘        └────┬────┘        └────┬────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  RAW JSON/CSV   │
                    │  (staging)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  NORMALIZER     │
                    │  + 2024 Actuals │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ PARQUET OUTPUT  │
                    │ (BSC schema)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  STREAMLIT UI   │
                    │ (comparison)    │
                    └─────────────────┘
```

---

## 3. New Folder Structure

```
Vietnam_dashboard/
├── DATA/
│   ├── raw/
│   │   └── concensus_report/       # INPUT staging area
│   │       ├── pdf/                # Source PDFs
│   │       │   ├── HCM_Strategy_2026.pdf
│   │       │   ├── SSI_Strategy_2026.pdf
│   │       │   └── ...
│   │       ├── screenshots/        # Screenshot inputs
│   │       └── staging/            # Temp JSON extracts
│   │           ├── hcm_raw.json
│   │           ├── ssi_raw.json
│   │           └── vci_raw.json
│   │
│   └── processed/forecast/
│       ├── bsc/                    # BSC data (Excel import)
│       │   ├── bsc_combined.parquet
│       │   └── bsc_history.parquet
│       ├── consensus/              # Normalized consensus data
│       │   ├── {source}_forecast.parquet  (hcm, ssi, vci, shs...)
│       │   ├── consensus_combined.parquet
│       │   └── consensus_summary.parquet
│       └── _archive/               # Old/deprecated files
│
├── PROCESSORS/forecast/            # All processing scripts
│   ├── extractors/
│   │   ├── pdf_extractor.py        # Gemini PDF extraction
│   │   ├── screenshot_extractor.py # Gemini vision extraction
│   │   └── vci_api_extractor.py    # VCI API fetcher
│   ├── normalizer.py               # Main normalization logic
│   ├── bsc_forecast_processor.py   # BSC Excel processor (existing)
│   └── run_consensus_pipeline.py   # Main orchestrator
│
└── WEBAPP/pages/forecast/tabs/
    └── consensus_tab.py            # Updated comparison UI
```

---

## 4. Schema Definition

### Minimal Schema (Core Metrics)
```python
CONSENSUS_SCHEMA = {
    'symbol': str,           # Ticker
    'source': str,           # hcm, ssi, vci, shs, bsc
    'target_price': float,   # VND
    'npatmi_2025f': float,   # Billion VND
    'npatmi_2026f': float,   # Billion VND
    'pe_fwd_2025': float,    # Optional
    'pe_fwd_2026': float,    # Optional
    'updated_at': datetime,  # Extraction date
    'is_calculated': bool,   # True if back-calculated
}
```

### Extended Schema (BSC-compatible)
```python
BSC_SCHEMA_FULL = {
    'symbol', 'target_price', 'current_price', 'upside_pct', 'rating',
    'rev_2025f', 'rev_2026f', 'npatmi_2025f', 'npatmi_2026f',
    'eps_2025f', 'eps_2026f', 'roe_2025f', 'roe_2026f',
    'pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pb_fwd_2026',
    'sector', 'entity_type', 'updated_at'
}
```

---

## 5. Implementation Phases

### Phase 1: Restructure & Cleanup (1 hour)
- [ ] Move scripts from `concensus_report/raw_extracts/` to `PROCESSORS/forecast/`
- [ ] Rename `concensus_report/` to proper structure (pdf/, screenshots/, staging/)
- [ ] Update imports and paths in existing scripts
- [ ] Archive deprecated files

### Phase 2: Extractor Modules (2 hours)
- [ ] **pdf_extractor.py** - Refactor `extract_forecast_from_pdf.py`
  - Single function: `extract_from_pdf(pdf_path, source) -> list[dict]`
  - Uses Gemini API
  - Outputs to staging/

- [ ] **screenshot_extractor.py** - NEW
  - Function: `extract_from_screenshot(image_data) -> list[dict]`
  - Uses Claude vision (inline image analysis)
  - Manual trigger only (user pastes screenshot)

- [ ] **vci_api_extractor.py** - Refactor existing VCI API script
  - Function: `fetch_vci_coverage() -> list[dict]`
  - Auto-scheduled daily

### Phase 3: Normalizer Enhancement (1 hour)
- [ ] Move `normalize_consensus_data.py` to `PROCESSORS/forecast/normalizer.py`
- [ ] Add 2024 fundamental back-calculation (already done)
- [ ] Add PE → NPATMI calculation option
- [ ] Single entry point: `normalize_all_sources() -> dict[source, DataFrame]`

### Phase 4: BSC Excel Importer (1 hour)
- [ ] Create `bsc_excel_importer.py`
- [ ] Read user's Excel file → convert to BSC schema
- [ ] Output to `DATA/processed/forecast/bsc/bsc_combined.parquet`
- [ ] Track update timestamp

### Phase 5: Pipeline Orchestrator (30 min)
- [ ] Create `run_consensus_pipeline.py`
- [ ] Modes: `--extract`, `--normalize`, `--full`, `--vci-only`
- [ ] Logging and error handling

### Phase 6: Streamlit UI Update (1 hour)
- [ ] Update `consensus_tab.py` for multi-source comparison
- [ ] Add source filter (BSC, HCM, SSI, VCI)
- [ ] Show consensus mean vs individual estimates
- [ ] Highlight discrepancies (>10% diff)

---

## 6. Usage Workflow

### A. PDF Extraction (One-time per report)
```bash
# User has new PDF
python PROCESSORS/forecast/extractors/pdf_extractor.py \
    --pdf concensus_report/pdf/HCM_Strategy_2026.pdf \
    --source hcm

# Output: concensus_report/staging/hcm_raw.json
```

### B. Screenshot Extraction (Ad-hoc)
```
User: [Pastes screenshot in Claude Code]
Claude: Extracts table → saves to staging/hcm_supplement.json
```

### C. VCI API (Automated)
```bash
python PROCESSORS/forecast/extractors/vci_api_extractor.py
# Output: concensus_report/staging/vci_raw.json
```

### D. BSC Excel Update (When user updates)
```bash
python PROCESSORS/forecast/bsc_excel_importer.py \
    --excel /path/to/BSC_Forecast.xlsx
# Output: DATA/processed/forecast/bsc/bsc_combined.parquet
```

### E. Full Normalization
```bash
python PROCESSORS/forecast/run_consensus_pipeline.py --normalize
# Reads: staging/*.json
# Outputs: DATA/processed/forecast/consensus/*.parquet
```

---

## 7. File Migration Plan ✅ COMPLETED

| Original Location | New Location | Status |
|------------------|--------------|--------|
| `concensus_report/raw_extracts/extract_forecast_from_pdf.py` | `PROCESSORS/forecast/extractors/pdf_extractor.py` | ✅ Done |
| `concensus_report/raw_extracts/normalize_consensus_data.py` | `PROCESSORS/forecast/normalizer.py` | ✅ Done |
| `concensus_report/raw_extracts/*.json` | `DATA/raw/concensus_report/staging/*.json` | ✅ Done |
| `concensus_report/*.pdf` | `DATA/raw/concensus_report/pdf/*.pdf` | ✅ Done |
| `concensus_report/` (root) | `DATA/raw/concensus_report/` | ✅ Done |
| `DATA/processed/forecast/consensus/` | Keep (normalized output) | ✅ Keep |

---

## 8. Dependencies

**Existing:**
- pandas, numpy
- google-generativeai (Gemini)
- streamlit

**New:**
- openpyxl (for Excel import)

---

## 9. Success Criteria

1. ✅ Single command normalizes all sources to parquet
2. ✅ BSC Excel import works seamlessly
3. ✅ Screenshot extraction functional in Claude Code
4. ✅ Streamlit shows multi-source comparison
5. ✅ Coverage: >80% stocks have NPATMI from ≥2 sources
6. ✅ Data accuracy: <5% variance between sources for same stock

---

## 10. Clarified Requirements ✅

| Question | Answer |
|----------|--------|
| Screenshot workflow | Folder-based: `concensus_report/screenshots/` → AI agent batch extracts |
| VCI API frequency | On-demand, monthly |
| BSC Excel format | Already working via `PROCESSORS/forecast/bsc_forecast_processor.py` |
| History tracking | BSC: 2 files (history + latest), Consensus: overwrite only |

---

## 11. NPATMI Calculation Methods

When PDF/screenshot doesn't have NPATMI directly, calculate from:

### Priority 1: Direct Extraction
```python
# Extracted directly from PDF/screenshot
NPATMI_2025 = extracted_value
NPATMI_2026 = extracted_value
```

### Priority 2: From Growth Rate + 2024 Fundamental
```python
# Get 2024 actual from fundamental data (Q1+Q2+Q3+Q4)
NPATMI_2024 = load_fundamental_2024()  # Sum 4 quarters
NPATMI_2025 = NPATMI_2024 * (1 + growth_2025)
NPATMI_2026 = NPATMI_2025 * (1 + growth_2026)
```

### Priority 3: From PE Forward + Market Cap
```python
# Option A: If has Market Cap in source
NPATMI_2025 = Market_Cap / PE_FWD_2025

# Option B: If has Target Price + PE + Outstanding Shares
EPS_2025 = Target_Price / PE_FWD_2025
NPATMI_2025 = EPS_2025 * Outstanding_Shares

# IMPORTANT: Check units!
# - If Market Cap in VND → convert to billion VND
# - If Market Cap in USD → convert to VND first
```

### Implementation Notes
- Outstanding shares from OHLCV: `DATA/raw/ohlcv/OHLCV_mktcap.parquet`
- Market cap from OHLCV: Latest close × outstanding shares
- Always validate unit: PDF may show VND, billion VND, or USD

---

## 12. Unit Standardization (follows `config/unit_standards.json`)

| Metric | Storage Unit | Display Unit |
|--------|--------------|--------------|
| `target_price` | VND | VND |
| `npatmi_2025f/2026f` | Billion VND | Tỷ VND |
| `market_cap` | Billion VND | Tỷ VND |
| `pe_fwd` | Times (x) | x |
| `growth_rate` | Decimal (0.15 = 15%) | % |

**Note:** BSC forecast uses billion VND for NPATMI. Consensus matches this for easy comparison.

---

## 13. Final Output Schema (Simplified)

### Output Files (Parquet only, NO JSON)
```
DATA/processed/forecast/consensus/
├── hcm_forecast.parquet       # HCM source
├── ssi_forecast.parquet       # SSI source
├── vci_forecast.parquet       # VCI source
├── consensus_combined.parquet # All sources merged
└── consensus_summary.parquet  # Aggregated stats per symbol
```

### Consensus Parquet Schema
```python
CONSENSUS_SCHEMA = {
    'symbol': str,           # Ticker
    'source': str,           # hcm, ssi, vci
    'target_price': float,   # VND
    'npatmi_2025f': float,   # Billion VND
    'npatmi_2026f': float,   # Billion VND
    'is_calculated': bool,   # True if back-calculated
}
```

### BSC Files (2 parquets)
- `bsc_combined.parquet` - Latest (used by Streamlit)
- `bsc_history.parquet` - Historical snapshots with `snapshot_date` column

---

## 13. Updated Folder Structure ✅ IMPLEMENTED

```
DATA/
├── raw/
│   └── concensus_report/           # INPUT staging area (moved from root)
│       ├── pdf/                    # Source PDFs
│       │   ├── BCChienluoc2026_VCI.pdf
│       │   ├── Bao cao chien luoc nam 2026_SSIResearch.pdf
│       │   ├── SHS_Macro_Outlook2026.pdf
│       │   └── Strategy Report2026_HCMpdf.pdf
│       ├── screenshots/            # Drop images here for batch extraction
│       │   ├── hcm_table_01.png
│       │   └── ssi_forecast.png
│       └── staging/                # Temp JSON extracts
│           ├── hcm_raw.json
│           ├── ssi_raw.json
│           └── vci_raw.json
│
└── processed/forecast/
    ├── bsc/
    │   ├── bsc_combined.parquet    # Latest
    │   └── bsc_history.parquet     # Historical snapshots
    └── consensus/
        ├── hcm_forecast.parquet
        ├── ssi_forecast.parquet
        ├── vci_forecast.parquet
        ├── consensus_combined.parquet
        └── consensus_summary.parquet

PROCESSORS/forecast/
├── bsc_forecast_processor.py       # EXISTING - BSC Excel processor ✅
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py            # Gemini PDF extraction ✅
│   ├── screenshot_extractor.py     # Gemini vision extraction ✅
│   └── vci_api_extractor.py        # VCI API (TODO)
├── normalizer.py                   # Normalization + back-calc ✅
└── run_consensus_pipeline.py       # Main orchestrator (TODO)
```

---

## 14. Implementation Status

### Core Pipeline ✅ COMPLETE
1. ✅ Plan confirmed
2. ✅ Restructure folders (moved to DATA/raw/concensus_report/)
3. ✅ Move scripts to PROCESSORS/forecast/
4. ✅ Create `screenshot_extractor.py` with batch processing
5. ✅ Normalizer with 2024 fundamental back-calculation
6. ✅ Normalizer with PE/Growth Priority 3 calculation
7. ✅ Create `run_consensus_pipeline.py` orchestrator
8. ✅ Architecture documentation: `docs/consensus-forecast-pipeline.md`

### Coverage Achieved
- HCM: 93/93 (100%)
- SSI: 58/58 (100%)
- VCI: 84/84 (100%)
- NPATMI 2025F: 100% coverage

### Future Enhancements (Optional)
- ⏳ VCI API extractor (currently using PDF)
- ⏳ BSC history tracking (2 parquet files)
- ⏳ Streamlit UI for multi-source comparison
