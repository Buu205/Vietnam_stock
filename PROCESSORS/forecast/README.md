# Consensus Forecast Pipeline

Trích xuất và chuẩn hóa dữ liệu dự báo từ nhiều nguồn (HCM, SSI, VCI, BSC).

## Quick Start

```bash
# Chạy full pipeline
python3 PROCESSORS/forecast/run_consensus_pipeline.py

# Validate kết quả
python3 PROCESSORS/forecast/run_consensus_pipeline.py --validate
```

---

## Folder Structure

```
DATA/
├── raw/concensus_report/           # INPUT
│   ├── pdf/                        # Drop PDF vào đây
│   ├── screenshots/                # Drop ảnh vào đây
│   └── staging/                    # JSON trung gian (auto)
│
└── processed/forecast/
    ├── bsc/                        # BSC data
    └── consensus/                  # OUTPUT (parquet)

PROCESSORS/forecast/
├── extractors/
│   ├── pdf_extractor.py            # Gemini PDF extraction
│   └── screenshot_extractor.py     # Gemini screenshot batch
├── normalizer.py                   # JSON → Parquet
├── bsc_forecast_processor.py       # BSC Excel processor
└── run_consensus_pipeline.py       # Main orchestrator
```

---

## Workflow

### 1. Thêm PDF mới

```bash
# Copy PDF vào folder
cp ~/Downloads/HCM_Strategy_2026.pdf DATA/raw/concensus_report/pdf/

# Extract (cần GEMINI_API_KEY)
export GEMINI_API_KEY=your_key
python3 PROCESSORS/forecast/extractors/pdf_extractor.py \
    --pdf DATA/raw/concensus_report/pdf/HCM_Strategy_2026.pdf \
    --source hcm

# Output: DATA/raw/concensus_report/staging/hcm_raw.json
```

### 2. Thêm Screenshots

```bash
# Copy ảnh (đặt tên: {source}_*.png)
cp hcm_table_01.png DATA/raw/concensus_report/screenshots/

# Batch extract
python3 PROCESSORS/forecast/extractors/screenshot_extractor.py

# Output: Merge vào staging/{source}_raw.json
```

### 3. Normalize → Parquet

```bash
python3 PROCESSORS/forecast/normalizer.py

# Output:
# - DATA/processed/forecast/consensus/hcm_forecast.parquet
# - DATA/processed/forecast/consensus/ssi_forecast.parquet
# - DATA/processed/forecast/consensus/vci_forecast.parquet
# - DATA/processed/forecast/consensus/consensus_combined.parquet
# - DATA/processed/forecast/consensus/consensus_summary.parquet
```

### 4. Full Pipeline (One Command)

```bash
# Extract PDF + Normalize + Validate
python3 PROCESSORS/forecast/run_consensus_pipeline.py --extract-pdf

# Extract Screenshots + Normalize + Validate
python3 PROCESSORS/forecast/run_consensus_pipeline.py --extract-screenshots

# Normalize only (default)
python3 PROCESSORS/forecast/run_consensus_pipeline.py
```

---

## NPATMI Calculation Priority

| Priority | Method | Điều kiện |
|----------|--------|-----------|
| 1 | Direct | Có NPATMI trực tiếp trong PDF |
| 2 | Growth + 2024 | Có growth_2025 + fundamental 2024 |
| 3 | PE-based | Có PE_FWD + Market Cap/Shares |
| 4 | BSC ref | Fallback từ BSC data |

---

## Check Results

```bash
# 1. List output files
ls -lh DATA/processed/forecast/consensus/

# 2. Quick check
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/forecast/consensus/consensus_combined.parquet')
print(f'Records: {len(df)}')
print(f'Tickers: {df.symbol.nunique()}')
print(f'NPATMI 2025F coverage: {df.npatmi_2025f.notna().mean()*100:.1f}%')
print(f'NPATMI 2026F coverage: {df.npatmi_2026f.notna().mean()*100:.1f}%')
"

# 3. Full validation
python3 PROCESSORS/forecast/run_consensus_pipeline.py --validate
```

---

## Output Schema

### consensus_combined.parquet

| Column | Type | Unit |
|--------|------|------|
| symbol | str | Ticker |
| source | str | hcm/ssi/vci |
| target_price | float | VND |
| npatmi_2025f | float | Billion VND |
| npatmi_2026f | float | Billion VND |
| is_calculated | bool | True if back-calculated |

---

## Current Coverage

```
NPATMI 2025F: 100.0%
NPATMI 2026F: 89.7%
Target Price: 97.9%

Multi-source:
- 1 source: 37 stocks
- 2 sources: 37 stocks
- 3+ sources: 41 stocks
```

---

## Environment

```bash
# Required
export GEMINI_API_KEY=your_api_key

# Dependencies
pip install pandas google-generativeai
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing GEMINI_API_KEY | `export GEMINI_API_KEY=xxx` |
| PDF extraction failed | Check file size < 50MB, try `--model gemini-2.5-flash` |
| Low 2026F coverage | PDF không có growth_2026 data |
| Duplicate entries | Auto-deduped, prefer non-None values |
