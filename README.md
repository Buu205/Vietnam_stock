# Vietnam Stock Dashboard

Vietnamese stock market financial data dashboard for 457 stocks across 19 sectors.

**Live:** [vietnamstock.streamlit.app](https://vietnamstock.streamlit.app)
**Repository:** [github.com/Buu205/Vietnam_stock](https://github.com/Buu205/Vietnam_stock)

---

## Features

| Feature | Description |
|---------|-------------|
| **Fundamental Analysis** | Company, Bank, Insurance, Security metrics |
| **Technical Analysis** | OHLCV, MA, RSI, MACD, Bollinger, ATR |
| **Valuation** | PE, PB, PS, EV/EBITDA (TTM & Forward) |
| **Sector Analysis** | FA+TA scoring with Buy/Sell/Hold signals |
| **BSC Forecast** | Analyst forecasts for 93 stocks |

---

## Quick Start

```bash
# Clone
git clone https://github.com/Buu205/Vietnam_stock.git
cd Vietnam_stock

# Install
pip install -r WEBAPP/requirements.txt

# Run
streamlit run WEBAPP/main_app.py
```

Dashboard runs at: http://localhost:8501

---

## Daily Data Update

```bash
# Run all updates (~2 minutes)
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

Pipeline order:
1. OHLCV data
2. Technical indicators
3. Macro & commodity
4. Valuation metrics
5. Sector analysis

---

## Project Structure

```
Vietnam_dashboard/
├── WEBAPP/              # Streamlit frontend (76 files)
│   ├── main_app.py      # Entry point
│   ├── pages/           # 7 dashboard pages
│   ├── services/        # Data services
│   └── core/            # Config, theme, models
│
├── PROCESSORS/          # Data processing (102 files)
│   ├── api/             # API clients
│   ├── fundamental/     # Financial calculators
│   ├── technical/       # TA indicators
│   ├── valuation/       # PE/PB/EV calculators
│   ├── sector/          # Sector analysis
│   └── pipelines/       # Daily orchestration
│
├── DATA/                # Data storage (~250 MB)
│   ├── raw/             # Input data
│   └── processed/       # Output data (parquet)
│
├── config/              # Configuration
│   └── registries/      # Metric, Sector registries
│
└── MCP_SERVER/          # MCP API (30 tools)
```

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| Company Analysis | Non-financial company metrics |
| Bank Analysis | Bank-specific ratios (27 banks) |
| Security Analysis | Brokerage company analysis |
| Sector Overview | FA+TA scoring by sector |
| Valuation | PE/PB/EV historical |
| Technical | Indicators, alerts, money flow |
| BSC Forecast | Forward PE/PB 2025-2026 |

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Tickers | 457 |
| Sectors | 19 |
| Entity Types | 4 (COMPANY, BANK, INSURANCE, SECURITY) |
| Financial Metrics | 2,099 |
| Calculated Formulas | 40+ |

---

## Data Sources

| Source | Data Type |
|--------|-----------|
| VNStock | OHLCV, market cap |
| WiChart | Exchange rates, commodities |
| Simplize | Vietnamese economic data |
| BSC Research | Analyst forecasts |

---

## Technology Stack

- **Frontend:** Streamlit, Plotly, Pydantic
- **Backend:** Python 3.13, Pandas, NumPy, TA-Lib
- **Storage:** Parquet files
- **Deployment:** Streamlit Cloud

---

## Documentation

| Document | Description |
|----------|-------------|
| [Project Overview](docs/project-overview-pdr.md) | Vision, requirements, roadmap |
| [System Architecture](docs/system-architecture.md) | Data flow, components |
| [Codebase Summary](docs/codebase-summary.md) | Module structure |
| [Code Standards](docs/code-standards.md) | Naming conventions, patterns |
| [CLAUDE.md](CLAUDE.md) | AI/Developer guidelines |

---

## Development

### Environment

- Python 3.13 (system installation)
- vnstock_data (global package)
- TA-Lib (system installation)

### Registry Usage

```python
from config.registries import MetricRegistry, SectorRegistry

# Metric lookup
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")

# Sector lookup
sector_reg = SectorRegistry()
info = sector_reg.get_ticker("ACB")
peers = sector_reg.get_peers("ACB")
```

### Data Paths (v4.0.0)

```python
# Canonical paths
input_path = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"
output_path = "DATA/processed/valuation/pe/historical_pe.parquet"
```

---

## License

Private repository - All rights reserved.

---

**Maintained by:** Buu Phan
**Contact:** [GitHub Issues](https://github.com/Buu205/Vietnam_stock/issues)
