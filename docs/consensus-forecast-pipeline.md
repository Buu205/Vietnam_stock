# Consensus Forecast Pipeline

Architecture & usage guide for extracting, normalizing, and comparing forecast data from multiple sources.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├────────────────┬────────────────┬────────────────┬──────────────┤
│     PDF        │   Screenshot   │    VCI API     │   BSC Excel  │
│  (Gemini AI)   │  (Gemini AI)   │   (monthly)    │  (manual)    │
└───────┬────────┴───────┬────────┴───────┬────────┴──────┬───────┘
        │                │                │               │
        ▼                ▼                ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA/raw/concensus_report/staging/                  │
│                    (JSON intermediate)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSORS/forecast/                          │
│                      normalizer.py                               │
│  ┌─────────────┬───────────────┬────────────────┐               │
│  │ Priority 1  │  Priority 2   │   Priority 3   │               │
│  │ Direct      │ Growth Rate   │   PE-based     │               │
│  │ Extraction  │ + 2024 Fund   │   Calculation  │               │
│  └─────────────┴───────────────┴────────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA/processed/forecast/consensus/                  │
│                    (Parquet output)                              │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐    │
│  │hcm_forecast  │ssi_forecast  │vci_forecast  │consensus_  │    │
│  │  .parquet    │  .parquet    │  .parquet    │combined    │    │
│  └──────────────┴──────────────┴──────────────┴────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
DATA/
├── raw/
│   └── concensus_report/           # INPUT: Raw data staging
│       ├── pdf/                    # Drop PDFs here
│       │   ├── HCM_Strategy_2026.pdf
│       │   ├── SSI_Strategy_2026.pdf
│       │   └── VCI_Strategy_2026.pdf
│       ├── screenshots/            # Drop screenshots here
│       │   └── hcm_table_01.png
│       └── staging/                # Extracted JSON (auto-generated)
│           ├── hcm_raw.json
│           ├── ssi_raw.json
│           └── vci_raw.json
│
└── processed/
    └── forecast/
        ├── bsc/                    # BSC data (separate processor)
        │   └── bsc_combined.parquet
        └── consensus/              # OUTPUT: Normalized parquet
            ├── hcm_forecast.parquet
            ├── ssi_forecast.parquet
            ├── vci_forecast.parquet
            ├── consensus_combined.parquet
            └── consensus_summary.parquet

PROCESSORS/forecast/
├── extractors/
│   ├── pdf_extractor.py           # Gemini PDF extraction
│   └── screenshot_extractor.py    # Gemini screenshot batch
├── normalizer.py                  # JSON → Parquet normalization
├── bsc_forecast_processor.py      # BSC Excel processor
└── run_consensus_pipeline.py      # Main orchestrator
```

---

## Quick Start

### 1. Add New PDF Report

```bash
# 1. Copy PDF to input folder
cp ~/Downloads/HCM_Strategy_2026.pdf DATA/raw/concensus_report/pdf/

# 2. Extract data (requires GEMINI_API_KEY)
export GEMINI_API_KEY=your_key
python3 PROCESSORS/forecast/extractors/pdf_extractor.py \
    --pdf DATA/raw/concensus_report/pdf/HCM_Strategy_2026.pdf \
    --source hcm

# 3. Run normalization
python3 PROCESSORS/forecast/normalizer.py
```

### 2. Add Screenshots

```bash
# 1. Copy screenshots to folder
cp ~/Downloads/hcm_table_*.png DATA/raw/concensus_report/screenshots/

# 2. Batch extract (naming: {source}_*.png)
python3 PROCESSORS/forecast/extractors/screenshot_extractor.py

# 3. Normalize
python3 PROCESSORS/forecast/normalizer.py
```

### 3. Full Pipeline (One Command)

```bash
# Extract + Normalize + Validate
python3 PROCESSORS/forecast/run_consensus_pipeline.py

# With PDF extraction
python3 PROCESSORS/forecast/run_consensus_pipeline.py --extract-pdf

# Validate only
python3 PROCESSORS/forecast/run_consensus_pipeline.py --validate
```

---

## NPATMI Calculation Priority

| Priority | Method | When Used |
|----------|--------|-----------|
| 1 | Direct Extraction | NPATMI directly in PDF/screenshot |
| 2 | Growth Rate + 2024 Fundamental | Has growth %, missing NPATMI |
| 3 | PE-based Calculation | Has PE forward, no growth data |
| 4 | BSC Reference Fallback | Cross-reference with BSC data |

### Priority 3 Details (PE Calculation)

```python
# Option A: Market Cap based
NPATMI_2025 = Market_Cap / PE_FWD_2025

# Option B: Target Price + Shares
EPS_2025 = Target_Price / PE_FWD_2025
NPATMI_2025 = EPS_2025 × Outstanding_Shares
```

---

## Unit Standards

| Metric | Storage Unit | Display |
|--------|--------------|---------|
| `target_price` | VND | VND |
| `npatmi_2025f/2026f` | Billion VND | Tỷ VND |
| `market_cap` | Billion VND | Tỷ VND |
| `pe_fwd` | Times (x) | x |
| `growth_rate` | Decimal | % |

---

## Output Schema

### consensus_combined.parquet

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | str | Ticker (VCB, ACB...) |
| `source` | str | hcm, ssi, vci |
| `target_price` | float | VND |
| `npatmi_2025f` | float | Billion VND |
| `npatmi_2026f` | float | Billion VND |
| `is_calculated` | bool | True if back-calculated |

### consensus_summary.parquet

Aggregated stats per symbol with mean/min/max across sources.

---

## Check Results

```bash
# 1. List output files
ls -lh DATA/processed/forecast/consensus/

# 2. Quick data check
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/forecast/consensus/consensus_combined.parquet')
print(f'Records: {len(df)}')
print(f'Tickers: {df.symbol.nunique()}')
print(df.head(10))
"

# 3. Full validation
python3 PROCESSORS/forecast/run_consensus_pipeline.py --validate
```

---

## Current Coverage (2026-01-03)

| Source | Total | NPATMI 2025F | Coverage |
|--------|-------|--------------|----------|
| HCM | 93 | 93 | 100% |
| SSI | 58 | 58 | 100% |
| VCI | 84 | 84 | 100% |
| **Combined** | 235 | 235 | **100%** |

Multi-source coverage:
- 1 source: 36 stocks
- 2 sources: 38 stocks
- 3+ sources: 41 stocks

---

## Troubleshooting

### Missing GEMINI_API_KEY
```bash
export GEMINI_API_KEY=your_api_key_here
```

### PDF Extraction Failed
- Check PDF is readable (not encrypted)
- Try different model: `--model gemini-2.5-flash`
- Check file size < 50MB

### Low NPATMI Coverage
- Ensure JSON has `npatmi_growth_2025` or `pe_fwd_2025`
- Check fundamental 2024 data exists for ticker
- Run with verbose: check `calc_note` field

---

## Related Files

- [Plan](../plans/2026-01-03-consensus-forecast-pipeline/plan.md)
- [BSC Processor](../PROCESSORS/forecast/bsc_forecast_processor.py)
- [Unit Standards](../config/unit_standards.json)
