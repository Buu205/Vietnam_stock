# 📊 Vietnam Stock Dashboard

**Repository:** https://github.com/Buu205/Vietnam_stock
**Live Dashboard:** [Streamlit Cloud](https://vietnamstock.streamlit.app) *(nếu đã deploy)*
**Last Updated:** 2025-12-18

---

## 🎯 Giới Thiệu

Vietnam Stock Dashboard là một ứng dụng phân tích tài chính toàn diện cho thị trường chứng khoán Việt Nam. Ứng dụng cung cấp:

- **Fundamental Analysis** - Phân tích tài chính doanh nghiệp (Company, Bank, Insurance, Security)
- **Valuation Metrics** - Định giá PE, PB, PS, EV/EBITDA theo TTM và Forward
- **Technical Analysis** - Chỉ báo kỹ thuật, tín hiệu giao dịch, market breadth
- **Sector Analysis** - Phân tích ngành với scoring và ranking
- **BSC Forecast** - Dự báo từ BSC Research với 93 mã cổ phiếu

---

## 🖥️ Dashboard Pages

| Page | Mô tả | Icon |
|------|-------|------|
| **Company Analysis** | Phân tích tài chính doanh nghiệp phi tài chính | 🏢 |
| **Bank Analysis** | Phân tích tài chính ngân hàng (27 banks) | 🏦 |
| **Security Analysis** | Phân tích công ty chứng khoán | 📈 |
| **Sector Overview** | Tổng quan ngành với FA+TA scoring | 🌐 |
| **Valuation** | PE/PB/PS/EV-EBITDA TTM + Historical | 💰 |
| **Technical Analysis** | Chỉ báo kỹ thuật, alerts, money flow | 📉 |
| **BSC Forecast** | Dự báo PE/PB Forward 2025-2026 từ BSC | 🎯 |

---

## 📁 Cấu Trúc Dự Án

```
Vietnam_dashboard/
│
├── WEBAPP/                          # 🌐 Streamlit Application
│   ├── main_app.py                  # Entry point (st.navigation)
│   ├── requirements.txt             # Dependencies
│   │
│   ├── pages/                       # Dashboard pages
│   │   ├── company/                 # Company analysis
│   │   ├── bank/                    # Bank analysis
│   │   ├── security/                # Security analysis
│   │   ├── sector/                  # Sector overview
│   │   ├── valuation/               # Valuation metrics
│   │   ├── technical/               # Technical analysis
│   │   └── forecast/                # BSC Forecast
│   │
│   ├── services/                    # Data loading services
│   │   ├── company_service.py       # Company data API
│   │   ├── bank_service.py          # Bank data API
│   │   ├── security_service.py      # Security data API
│   │   ├── sector_service.py        # Sector data API
│   │   ├── valuation_service.py     # Valuation data API
│   │   ├── technical_service.py     # Technical data API
│   │   └── forecast_service.py      # BSC Forecast API
│   │
│   ├── core/                        # Core utilities
│   │   ├── styles.py                # Midnight Financial Terminal theme
│   │   ├── theme.py                 # Color palette & typography
│   │   ├── data_paths.py            # Centralized data paths
│   │   └── models/                  # Pydantic data models
│   │
│   └── components/                  # Reusable UI components
│
├── PROCESSORS/                      # 🔧 Data Processing Pipeline
│   ├── pipelines/                   # Daily update orchestrators
│   │   ├── run_all_daily_updates.py # Master pipeline
│   │   ├── daily_ohlcv_update.py    # OHLCV data
│   │   ├── daily_ta_complete.py     # Technical analysis
│   │   ├── daily_valuation.py       # Valuation metrics
│   │   ├── daily_macro_commodity.py # Macro & commodity
│   │   └── daily_sector_analysis.py # Sector scoring
│   │
│   ├── fundamental/                 # Financial calculators
│   │   └── calculators/
│   │       ├── company_calculator.py
│   │       ├── bank_calculator.py
│   │       ├── insurance_calculator.py
│   │       └── security_calculator.py
│   │
│   ├── technical/                   # Technical indicators
│   │   ├── indicators/              # MA, RSI, MACD, Bollinger, ATR
│   │   ├── market_breadth/          # Advance/Decline, McClellan
│   │   └── money_flow/              # Money flow analysis
│   │
│   ├── valuation/                   # Valuation calculators
│   │   └── calculators/
│   │       ├── pe_calculator.py
│   │       ├── pb_calculator.py
│   │       ├── ps_calculator.py
│   │       ├── ev_ebitda_calculator.py
│   │       └── vnindex_pe_calculator.py
│   │
│   ├── sector/                      # Sector analysis
│   │   ├── sector_aggregator.py
│   │   └── sector_scorer.py
│   │
│   └── forecast/                    # BSC Forecast
│       ├── bsc_forecast_processor.py
│       └── update_bsc_excel.py
│
├── DATA/                            # 📊 Data Storage
│   ├── raw/                         # Input data
│   │   ├── ohlcv/                   # OHLCV + Market Cap
│   │   ├── fundamental/             # Financial statements (CSV)
│   │   ├── commodity/               # Gold, Oil prices
│   │   └── macro/                   # Interest rates, FX
│   │
│   └── processed/                   # Output data (Parquet)
│       ├── fundamental/             # Financial metrics
│       │   ├── company/             # 37,145 rows
│       │   ├── bank/                # 1,051 rows
│       │   ├── insurance/           # 418 rows
│       │   └── security/            # 2,811 rows
│       │
│       ├── valuation/               # Valuation historical
│       │   ├── pe/historical/       # 789,611 rows
│       │   ├── pb/historical/       # 789,611 rows
│       │   ├── ps/historical/       # P/S ratio
│       │   ├── ev_ebitda/           # EV/EBITDA
│       │   └── vnindex/             # VN-Index valuation
│       │
│       ├── technical/               # Technical indicators
│       │   ├── basic_data.parquet   # 89,821 rows
│       │   ├── alerts/              # Trading signals
│       │   ├── market_breadth/      # Market breadth
│       │   ├── money_flow/          # Money flow by sector
│       │   └── vnindex/             # VN-Index indicators
│       │
│       ├── sector/                  # Sector analysis
│       │   ├── sector_combined_scores.parquet
│       │   ├── sector_fundamental_metrics.parquet
│       │   └── sector_valuation_metrics.parquet
│       │
│       ├── forecast/bsc/            # BSC Forecast
│       │   ├── bsc_individual.parquet    # 93 stocks
│       │   ├── bsc_sector_valuation.parquet
│       │   └── bsc_combined.parquet
│       │
│       └── macro_commodity/         # Macro & commodity
│           └── macro_commodity_unified.parquet
│
├── config/                          # ⚙️ Configuration
│   ├── registries/                  # Registry classes
│   │   ├── metric_lookup.py         # MetricRegistry
│   │   └── sector_lookup.py         # SectorRegistry
│   ├── schema_registry/             # Schema definitions
│   ├── metadata/                    # Ticker details, mappings
│   └── business_logic/              # Business rules
│
└── docs/                            # 📚 Documentation
    ├── Formula/                     # Formula reference
    └── archive/                     # Historical docs
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Buu205/Vietnam_stock.git
cd Vietnam_stock
```

### 2. Install Dependencies

```bash
pip install -r WEBAPP/requirements.txt
```

### 3. Run Dashboard

```bash
streamlit run WEBAPP/main_app.py
```

Dashboard sẽ chạy tại: http://localhost:8501

---

## 🔄 Daily Data Update

### One-Command Update (Recommended)

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Pipeline thực hiện theo thứ tự:**

1. **OHLCV** → Raw market data (OHLC + Volume + Market Cap)
2. **Technical Analysis** → TA indicators, alerts, breadth, money flow
3. **Macro & Commodity** → Economic data (gold, USD/VND, rates)
4. **Stock Valuation** → PE/PB/EV-EBITDA + VNINDEX valuation
5. **Sector Analysis** → Sector metrics, scores, signals

**Thời gian chạy:** ~80-100 giây

### Individual Updates

```bash
# OHLCV data
python3 PROCESSORS/pipelines/daily_ohlcv_update.py

# Technical analysis
python3 PROCESSORS/pipelines/daily_ta_complete.py

# Valuation metrics
python3 PROCESSORS/pipelines/daily_valuation.py

# BSC Forecast (khi có Excel mới)
python3 PROCESSORS/forecast/update_bsc_excel.py
```

---

## 📊 Data Sources

### Fundamental Data

| Entity | File | Records | Key Metrics |
|--------|------|---------|-------------|
| Company | `company_financial_metrics.parquet` | 37,145 | ROE, ROA, EPS, Gross Margin, Net Margin |
| Bank | `bank_financial_metrics.parquet` | 1,051 | NIM, CIR, NPL Ratio, LDR, CAR |
| Insurance | `insurance_financial_metrics.parquet` | 418 | Combined Ratio, Claims Ratio |
| Security | `security_financial_metrics.parquet` | 2,811 | Brokerage Revenue, Trading Income |

### Valuation Data

| Metric | File | Records | Formula |
|--------|------|---------|---------|
| PE TTM | `historical_pe.parquet` | 789,611 | Market Cap / TTM Earnings |
| PB TTM | `historical_pb.parquet` | 789,611 | Market Cap / Book Value |
| P/S | `historical_ps.parquet` | - | Market Cap / TTM Revenue |
| EV/EBITDA | `historical_ev_ebitda.parquet` | - | Enterprise Value / EBITDA |
| VN-Index PE | `vnindex_valuation_refined.parquet` | - | Sum(MCap) / Sum(Earnings) |

### BSC Forecast Data

| File | Records | Description |
|------|---------|-------------|
| `bsc_individual.parquet` | 93 | Individual stocks với PE/PB Forward 2025-2026 |
| `bsc_sector_valuation.parquet` | 15 | Sector-level PE/PB Forward (ICB L2) |

**Sector classification:** ICB L2 Vietnamese sectors (Ngân hàng, Bất động sản, etc.)

---

## 🎨 Theme & Styling

Dashboard sử dụng **Midnight Financial Terminal** theme:

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark Navy | `#0D1117` |
| Surface | Elevated | `#161B22` |
| Primary | Brand Teal | `#009B87` |
| Accent | Bright Teal | `#00C9AD` |
| Warning | Gold | `#FFC132` |
| Text Primary | White | `#F0F4F8` |
| Text Muted | Slate | `#94A3B8` |

**Font:** IBM Plex Mono (monospace, professional)

---

## 📈 Key Features

### 1. BSC Forecast Dashboard

- **93 stocks** với target price, upside %, rating
- **PE/PB Forward 2025-2026** (individual + sector)
- **PE TTM vs FWD comparison** chart
- **PB TTM vs FWD comparison** chart
- **Sector Opportunity Score** (weighted scoring)
- **9M Achievement tracking** (YTD vs Full-year forecast)

### 2. Valuation Dashboard

- **Historical PE/PB/PS/EV-EBITDA** time series
- **VN-Index PE** với percentile ranking
- **Sector PE comparison** across 19 sectors
- **Individual stock screening** by valuation

### 3. Sector Dashboard

- **FA + TA Combined Score** for each sector
- **Buy/Sell/Hold signals** based on scoring
- **Sector rotation analysis**
- **Money flow by sector**

### 4. Technical Dashboard

- **Market Breadth** (Advance/Decline, McClellan Oscillator)
- **Trading Alerts** (MA Crossover, Breakout, Volume Spike)
- **VN-Index Technical Indicators**
- **Sector Breadth Analysis**

---

## 🔧 Configuration

### Environment Variables

```bash
# Data path (optional - defaults to project root)
export DATA_DIR=/path/to/data
```

### Streamlit Secrets (Production)

```toml
# .streamlit/secrets.toml
[DATA]
path = "DATA/"
```

---

## 📝 Development Workflow

### Local Development

```bash
# 1. Update data
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# 2. Run Streamlit
streamlit run WEBAPP/main_app.py

# 3. Make changes, hot-reload active
```

### Production Deployment

1. Push code to GitHub
2. Streamlit Cloud auto-deploys
3. Data files committed to repo (in processed/)

---

## 📚 Documentation

| File | Description |
|------|-------------|
| [CLAUDE.md](CLAUDE.md) | AI/Developer guidelines, project rules |
| [PROCESSORS/README.md](PROCESSORS/README.md) | Processing pipeline details |
| [docs/Formula/](docs/Formula/) | Formula reference & calculation guides |

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Follow existing code patterns
4. Update documentation
5. Submit pull request

---

## 📄 License

Private repository - All rights reserved.

---

**Maintained by:** Buu Phan
**Contact:** [GitHub Issues](https://github.com/Buu205/Vietnam_stock/issues)
