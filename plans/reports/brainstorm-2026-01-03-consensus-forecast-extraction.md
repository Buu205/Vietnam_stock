# Brainstorm: Consensus Forecast Data Extraction from Strategy Reports

**Date:** 2026-01-03
**Topic:** Extract stock forecasts from multiple securities company reports to build consensus table
**Status:** Brainstorm Complete

---

## Problem Statement

**Goal:** Extract forecast data từ các báo cáo chiến lược (PDF) của nhiều CTCK để tạo bảng consensus comparison tương tự BSC vs VCI hiện có.

**Current State:**
- BSC data: `DATA/processed/forecast/bsc/bsc_combined.parquet` (32 cols, structured)
- VCI data: `DATA/processed/forecast/vci/vci_coverage_universe.parquet` (30 cols, API-based)
- Consensus Tab: `WEBAPP/pages/forecast/tabs/consensus_tab.py` (BSC vs VCI only)

**New Sources (PDFs):**
| Source | File | Size |
|--------|------|------|
| VCI | BCChienluoc2026_VCI.pdf | 8.5MB |
| SSI | Bao cao chien luoc nam 2026_2025.10.09_SSIResearch.pdf | 2.7MB |
| SHS | SHS_Macro_Outlook2026.pdf | 38MB |
| HCM | Strategy Report2026_HCMpdf.pdf | 15MB |

**Target Metrics to Extract:**
- Ticker/Symbol
- NPATMI (LNST) forecast 2025F, 2026F
- PE forward 2025F, 2026F
- PB forward 2025F, 2026F
- % Growth 2025-2026 (NPATMI, Revenue)
- Target Price, Rating (nếu có)

---

## Evaluated Approaches

### Approach 1: AI Vision Extraction (Gemini/Claude)

**Method:** Dùng `ai-multimodal` skill (Gemini API) để đọc PDF và extract tables.

**Pros:**
- Handle complex table layouts, Vietnamese text
- Can understand context, merge split tables
- No code needed cho mỗi PDF format
- One-time extraction, manual review

**Cons:**
- Token cost cao cho PDF lớn (38MB SHS)
- Accuracy varies, cần manual validation
- Not automated/repeatable

**Implementation:**
```python
# Using ai-multimodal skill
from skills.ai_multimodal import analyze_pdf

result = analyze_pdf(
    pdf_path="concensus_report/BCChienluoc2026_VCI.pdf",
    prompt="""
    Extract all stock forecast tables with columns:
    - Ticker, NPATMI 2025F, NPATMI 2026F, PE 2025F, PE 2026F,
    - PB 2025F, PB 2026F, Growth %, Target Price, Rating
    Return as JSON array.
    """
)
```

**Effort:** Low (2-4 hours)
**Accuracy:** ~80-90% (needs validation)

---

### Approach 2: Python PDF Table Extraction

**Method:** Dùng libraries như `pdfplumber`, `camelot-py`, hoặc `tabula-py`.

**Pros:**
- Automated, repeatable
- No API costs
- Good for well-structured tables

**Cons:**
- Fragile - mỗi PDF layout cần tuning riêng
- Vietnamese text encoding issues
- Complex tables (merged cells) fail often
- Development time cao

**Implementation:**
```python
import pdfplumber
import camelot

# pdfplumber - good for simple tables
with pdfplumber.open("report.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()

# camelot - better for complex tables
tables = camelot.read_pdf("report.pdf", pages="all", flavor="lattice")
```

**Effort:** High (1-2 days per PDF format)
**Accuracy:** ~70-85% (depends on PDF quality)

---

### Approach 3: Hybrid - AI First, Code Validation

**Method:**
1. AI (Gemini) extract raw data từ PDF
2. Python script validate và normalize
3. Manual review outliers

**Pros:**
- Balance accuracy vs effort
- AI handles layout complexity
- Code ensures consistency
- Repeatable workflow

**Cons:**
- Still needs API costs
- Two-step process

**Implementation:**
```
concensus_report/
├── raw_extracts/           # AI extracted JSON
│   ├── vci_raw.json
│   ├── ssi_raw.json
│   └── ...
├── normalized/             # After validation
│   └── consensus_all.parquet
└── scripts/
    ├── extract_with_ai.py
    └── normalize_validate.py
```

**Effort:** Medium (4-8 hours)
**Accuracy:** ~90-95%

---

### Approach 4: Semi-Manual Excel Workflow

**Method:**
1. Open PDF, manually copy tables to Excel
2. Standardize column names
3. Python script merge to parquet

**Pros:**
- Most accurate (human verification)
- Simple, no tech complexity
- One-time effort for annual reports

**Cons:**
- Labor intensive
- Human error possible
- Not scalable

**Effort:** High (2-3 hours manual work)
**Accuracy:** ~98%

---

## Recommended Solution: Approach 3 (Hybrid)

**Rationale:**
- Strategy reports = annual, one-time extraction acceptable
- AI handles Vietnamese + complex tables well
- Validation script catches errors
- Balance between effort vs accuracy

### Implementation Plan

#### Phase 1: AI Extraction (2 hours)
```bash
# For each PDF, use Gemini vision
python3 scripts/extract_forecast_ai.py --source vci --pdf "concensus_report/BCChienluoc2026_VCI.pdf"
python3 scripts/extract_forecast_ai.py --source ssi --pdf "concensus_report/Bao cao chien luoc nam 2026*.pdf"
# ... etc
```

Output: `concensus_report/raw_extracts/{source}_raw.json`

#### Phase 2: Normalize & Validate (2 hours)
```python
# normalize_forecast.py
SCHEMA = {
    'ticker': str,
    'source': str,           # vci, ssi, shs, hcm
    'npatmi_2025f': float,   # billion VND
    'npatmi_2026f': float,
    'pe_fwd_2025': float,
    'pe_fwd_2026': float,
    'pb_fwd_2025': float,
    'pb_fwd_2026': float,
    'npatmi_growth_2025': float,  # decimal
    'npatmi_growth_2026': float,
    'target_price': float,
    'rating': str,
    'updated_at': datetime
}
```

#### Phase 3: Build Consensus Table (2 hours)
```python
# consensus_builder.py
def build_consensus(sources: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge all sources, calculate:
    - consensus_npatmi = mean across sources
    - consensus_pe = mean PE
    - spread = max - min (shows disagreement)
    - source_count = number of analysts covering
    """
```

Output: `DATA/processed/forecast/consensus/consensus_combined.parquet`

#### Phase 4: Update UI (2 hours)
- Extend `consensus_tab.py` to show multi-source comparison
- Add source filter (BSC, VCI, SSI, SHS, HCM)
- Show consensus vs individual estimates

---

## Data Schema Comparison

| Field | BSC | VCI | Normalized |
|-------|-----|-----|------------|
| Symbol | `symbol` | `ticker` | `ticker` |
| NPATMI 2025 | `npatmi_2025f` | `npatmi_2025F` | `npatmi_2025f` |
| NPATMI 2026 | `npatmi_2026f` | `npatmi_2026F` | `npatmi_2026f` |
| PE 2025 | `pe_fwd_2025` | `pe_2025F` | `pe_fwd_2025` |
| PE 2026 | `pe_fwd_2026` | `pe_2026F` | `pe_fwd_2026` |
| PB 2025 | `pb_fwd_2025` | `pb_2025F` | `pb_fwd_2025` |
| PB 2026 | `pb_fwd_2026` | `pb_2026F` | `pb_fwd_2026` |
| Growth 2025 | `npatmi_growth_yoy_2025` | `npatmiGrowth_2025F` | `npatmi_growth_2025` |
| Growth 2026 | `npatmi_growth_yoy_2026` | `npatmiGrowth_2026F` | `npatmi_growth_2026` |
| Target | `target_price` | `targetPrice` | `target_price` |
| Rating | `rating` | `rating` | `rating` |

---

## Available Tools/Skills

| Tool | Purpose | Recommended |
|------|---------|-------------|
| `ai-multimodal` skill | Gemini PDF analysis | **Yes** |
| `pdfplumber` | Python PDF extraction | Backup |
| `camelot-py` | Table extraction | Backup |
| `tabula-py` | PDF tables | Backup |

---

## Success Metrics

1. **Coverage:** Extract data for 80%+ of BSC tickers từ ít nhất 2 sources khác
2. **Accuracy:** <5% variance when comparing overlapping tickers
3. **Completeness:** PE, PB, NPATMI for 2025F & 2026F
4. **Freshness:** Updated within Q4/2025 reports

---

## Next Steps

1. **Confirm approach** với user (Hybrid recommended)
2. **Create extraction script** using `ai-multimodal` skill
3. **Run extraction** on 4 PDFs
4. **Validate & normalize** data
5. **Update consensus_tab.py** for multi-source view

---

## Unresolved Questions

1. **Unit consistency:** PDF tables có thể dùng đơn vị khác (tỷ VND vs triệu VND) - cần xác nhận
2. **Partial coverage:** Nếu source chỉ có PE không có NPATMI, xử lý thế nào?
3. **Rating mapping:** Mỗi CTCK dùng rating scale khác (BUY/MUA/OUTPERFORM) - cần mapping table
4. **Update frequency:** Strategy reports = annual, nhưng có update quarterly không?
5. **Priority weighting:** Có nên weight theo reputation (BSC/VCI > SHS/HCM)?

---

## Appendix: File Locations

```
concensus_report/                    # Source PDFs
├── BCChienluoc2026_VCI.pdf
├── Bao cao chien luoc nam 2026_2025.10.09_SSIResearch.pdf
├── SHS_Macro_Outlook2026.pdf
└── Strategy Report2026_HCMpdf.pdf

DATA/processed/forecast/             # Existing data
├── bsc/bsc_combined.parquet
├── vci/vci_coverage_universe.parquet
└── consensus/                       # NEW - to create
    ├── ssi_forecast.parquet
    ├── shs_forecast.parquet
    ├── hcm_forecast.parquet
    └── consensus_combined.parquet

WEBAPP/pages/forecast/tabs/
└── consensus_tab.py                 # Update for multi-source
```
