# Project Overview & PDR

**Project:** Vietnam Stock Dashboard
**Version:** 4.0.0
**Last Updated:** 2025-12-21

---

## 1. Executive Summary

Vietnamese stock market financial data dashboard providing comprehensive analysis for 457 stocks across 19 sectors. Built with Streamlit frontend and Python data processing pipelines.

### Key Capabilities
- **Fundamental Analysis** - Company, Bank, Insurance, Security financial metrics
- **Technical Analysis** - OHLCV, indicators (MA, RSI, MACD, Bollinger, ATR)
- **Valuation Metrics** - PE, PB, PS, EV/EBITDA (TTM & Forward)
- **Sector Analysis** - FA+TA scoring with Buy/Sell/Hold signals
- **BSC Forecast** - Analyst forecasts for 93 stocks

---

## 2. Target Users

| User Type | Primary Use Case |
|-----------|------------------|
| Retail Investors | Stock screening, valuation comparison |
| Financial Analysts | Sector analysis, fundamental research |
| Portfolio Managers | Sector rotation, money flow tracking |
| Quant Developers | Data pipeline, API integration |

---

## 3. Technology Stack

### Frontend
- **Streamlit** 1.36+ (multi-page navigation)
- **Plotly** (interactive charts)
- **Pydantic** (data validation)

### Backend/Processing
- **Python** 3.13 (system installation)
- **Pandas/NumPy** (data manipulation)
- **TA-Lib** (technical indicators)
- **Parquet** (data storage)

### Data Sources
| Source | Data Type |
|--------|-----------|
| VNStock | OHLCV, market cap |
| WiChart | Exchange rates, commodities |
| Simplize | Vietnamese economic data |
| BSC Research | Analyst forecasts |

### Deployment
- **Streamlit Cloud** (production)
- **GitHub** (source control)

---

## 4. Project Metrics

| Metric | Value |
|--------|-------|
| Total Tickers | 457 |
| Sectors | 19 (ICB L2 Vietnamese) |
| Entity Types | 4 (COMPANY, BANK, INSURANCE, SECURITY) |
| Financial Metrics | 2,099 mapped |
| Calculated Formulas | 40+ |
| Python Files | 196 |
| Data Storage | ~250 MB (Parquet) |

---

## 5. Feature Roadmap

### Completed (v4.0.0)
- [x] Registry system (Metric, Sector, Schema)
- [x] Financial calculators (4 entity types)
- [x] Technical indicators pipeline
- [x] Valuation calculators (PE/PB/PS/EV-EBITDA)
- [x] Daily update pipelines
- [x] BSC forecast integration
- [x] MCP Server (30 tools)

### In Progress
- [ ] Path migration to v4.0.0 canonical structure
- [ ] FA+TA Sector Analysis orchestration layer
- [ ] Unified sector dashboard

### Planned
- [ ] Configuration UI for FA/TA weights
- [ ] Real-time data updates
- [ ] Alert notifications
- [ ] Mobile-responsive design

---

## 6. Data Coverage

### Fundamental Data
| Entity | Tickers | Records | Key Metrics |
|--------|---------|---------|-------------|
| Company | 1,633 | 37,145 | ROE, ROA, EPS, margins |
| Bank | 46 | 1,033 | NIM, CIR, NPL, LDR, CAR |
| Insurance | 18 | 418 | Combined ratio, claims |
| Security | 146 | 2,811 | Brokerage revenue |

### Valuation Data
| Metric | Records | Formula |
|--------|---------|---------|
| PE TTM | 789,611 | Market Cap / TTM Earnings |
| PB TTM | 789,611 | Market Cap / Book Value |
| PS TTM | - | Market Cap / TTM Revenue |
| EV/EBITDA | - | Enterprise Value / EBITDA |

### Technical Data
- OHLCV: 89,821 records
- Indicators: SMA, RSI, MACD, Bollinger, ATR
- Alerts: Breakout, MA crossover, volume spike
- Money flow: Individual & sector level

---

## 7. Dashboard Pages

| Page | Icon | Description |
|------|------|-------------|
| Company Analysis | 🏢 | Non-financial company metrics |
| Bank Analysis | 🏦 | Bank-specific ratios (27 banks) |
| Security Analysis | 📈 | Brokerage company analysis |
| Sector Overview | 🌐 | FA+TA scoring by sector |
| Valuation | 💰 | PE/PB/EV historical & comparison |
| Technical | 📉 | Indicators, alerts, money flow |
| BSC Forecast | 🎯 | Forward PE/PB 2025-2026 |

---

## 8. Success Criteria

### Performance
- Dashboard load time < 3 seconds
- Daily update pipeline < 2 minutes
- Data refresh lag < 1 trading day

### Data Quality
- 100% ticker coverage in registries
- < 5% missing fundamental data
- Valuation metrics match external sources

### User Experience
- Intuitive navigation
- Mobile-responsive charts
- Export to Excel/CSV

---

## 9. Constraints & Dependencies

### Technical Constraints
- Python 3.13 (system installation, no virtualenv)
- Global vnstock_data package
- TA-Lib requires system installation

### Data Dependencies
- BSC Excel file for forecast updates
- VNStock API availability
- WiChart/Simplize API rate limits

### Deployment
- Streamlit Cloud free tier limits
- Data files committed to repo (< 100 MB each)

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limiting | Caching, retry with backoff |
| Data quality issues | Validators at input/output |
| Large file sizes | Parquet compression |
| Breaking changes | Registry versioning |

---

## Related Documents

- [System Architecture](system-architecture.md)
- [Codebase Summary](codebase-summary.md)
- [Code Standards](code-standards.md)
