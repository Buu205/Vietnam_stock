# 📊 Vietnam Stock Dashboard - Streamlit App

**Repository:** https://github.com/Buu205/Vietnam_stock  
**Purpose:** Streamlit dashboard để hiển thị dữ liệu chứng khoán Việt Nam

---

## 🎯 MỤC ĐÍCH REPOSITORY

Repository này **chỉ chứa code Streamlit (WEBAPP)** để deploy lên Streamlit Cloud.

**KHÔNG bao gồm:**
- ❌ `PROCESSORS/` - Logic tính toán (chạy local)
- ❌ `DATA/raw/` - Dữ liệu thô (lưu local)

**BAO GỒM:**
- ✅ `WEBAPP/` - Code Streamlit để hiển thị
- ✅ `config/` - Cấu hình hệ thống
- ✅ `docs/` - Tài liệu

---

## 📋 CẤU TRÚC REPOSITORY

```
Vietnam_dashboard/
├── WEBAPP/                 # ✅ Streamlit app (được push lên GitHub)
│   ├── main_app.py        # Entry point
│   ├── pages/             # Dashboard pages
│   ├── components/        # UI components
│   └── services/          # Data loading services
│
├── PROCESSORS/            # Core data processing
│   ├── pipelines/         # 🆕 Daily update scripts (consolidated)
│   │   ├── run_all_daily_updates.py  # Master orchestrator
│   │   ├── daily_ohlcv_update.py
│   │   ├── daily_ta_complete.py
│   │   ├── daily_macro_commodity.py
│   │   ├── daily_valuation.py
│   │   └── daily_sector_analysis.py
│   ├── core/              # Shared utilities
│   ├── fundamental/       # Financial metrics calculators
│   ├── technical/         # Technical analysis indicators
│   ├── valuation/         # Valuation metrics (PE/PB/EV-EBITDA)
│   └── sector/            # Sector aggregation & scoring
│
├── DATA/
│   ├── raw/               # Input data
│   │   ├── ohlcv/
│   │   ├── fundamental/
│   │   └── ...
│   └── processed/         # Output data
│       ├── fundamental/
│       ├── technical/
│       ├── valuation/
│       └── sector/
│
├── config/                # ✅ Configuration & registries
│   ├── registries/        # Python registry classes
│   ├── schema_registry/   # Schema definitions
│   └── metadata/          # Lookup data
│
└── docs/                  # ✅ Documentation
    ├── CURRENT/           # Active documentation
    ├── Formula/           # Formula reference
    └── archive/           # Historical docs
```

---

## 🚀 SETUP & DEPLOYMENT

### 1. Clone Repository
```bash
git clone https://github.com/Buu205/Vietnam_stock.git
cd Vietnam_stock
```

### 2. Install Dependencies
```bash
pip install -r WEBAPP/requirements.txt
```

### 3. Run Locally
```bash
streamlit run WEBAPP/main.py
```

### 4. Deploy to Streamlit Cloud
1. Connect repository to Streamlit Cloud
2. Set main file: `WEBAPP/main.py`
3. Deploy!

---

## 🔄 DAILY DATA UPDATES

### One-Command Update (Recommended)

```bash
# Run all daily updates in correct order
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Pipeline Order:**
1. **OHLCV** → Raw market data (OHLC + Volume + Market Cap)
2. **Technical Analysis** → TA indicators, alerts, breadth, money flow
3. **Macro & Commodity** → Economic data (gold, USD/VND, rates)
4. **Stock Valuation** → PE/PB/EV-EBITDA + VNINDEX valuation
5. **Sector Analysis** → Sector metrics, scores, signals

**Total Runtime:** ~80 seconds (~1.3 minutes)

### Individual Updates

```bash
# Run specific updates
python3 PROCESSORS/pipelines/daily_ohlcv_update.py
python3 PROCESSORS/pipelines/daily_ta_complete.py
python3 PROCESSORS/pipelines/daily_macro_commodity.py
python3 PROCESSORS/pipelines/daily_valuation.py
python3 PROCESSORS/pipelines/daily_sector_analysis.py
```

**For more details:** See [PROCESSORS/pipelines/README.md](PROCESSORS/pipelines/README.md)

---

## 📊 DATA SOURCE

**Lưu ý:** Repository này **KHÔNG chứa data files**.

### Option 1: Data từ Local (Development)
- Chạy `PROCESSORS/` local để tạo parquet files
- Streamlit đọc từ `DATA/processed/` (local path)

### Option 2: Data từ External Storage (Production)
- Upload parquet files lên S3/Google Drive
- Streamlit đọc từ external URL
- Hoặc sử dụng Streamlit Secrets để config data path

### Option 3: Data từ GitHub Releases
- Tạo GitHub Release với parquet files
- Streamlit download từ release assets

---

## 🔧 CONFIGURATION

### Environment Variables
```bash
# Data path (nếu data ở local)
export DATA_DIR=/path/to/data

# Hoặc config trong Streamlit Secrets
# .streamlit/secrets.toml
[DATA]
path = "s3://bucket/data/"
```

---

## 📝 WORKFLOW

### Development (Local)
```bash
# 1. Update all data (daily)
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# 2. Run Streamlit app
streamlit run WEBAPP/main_app.py
```

### Production (Streamlit Cloud)
```bash
# 1. Code auto-deploys from GitHub
# 2. Streamlit loads data from external source (S3/Drive)
# 3. Dashboard displays data
```

---

## 🎯 NOTES

- **Repository này chỉ để deploy Streamlit**, không chứa processing logic
- **Processing logic** chạy local để tạo parquet files
- **Parquet files** có thể upload riêng hoặc lưu external storage
- **Streamlit** chỉ đọc và hiển thị, không tính toán

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - AI/Developer guidelines
- **[PROCESSORS/pipelines/README.md](PROCESSORS/pipelines/README.md)** - Daily update pipeline details
- **[docs/CURRENT/](docs/CURRENT/)** - Active documentation
- **[docs/Formula/](docs/Formula/)** - Formula reference & guides

---

**Last Updated:** 2025-12-15
**Status:** ✅ Optimized with consolidated daily pipeline