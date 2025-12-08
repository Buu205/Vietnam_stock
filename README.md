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
├── WEBAPP/              # ✅ Streamlit app (được push lên GitHub)
│   ├── main.py         # Entry point
│   ├── pages/          # Dashboard pages
│   ├── components/     # UI components
│   └── services/       # Data loading services
│
├── config/             # ✅ Configuration files
│   └── schemas/        # Data schemas
│
├── docs/               # ✅ Documentation
│   ├── ARCHITECTURE_*.md
│   └── ...
│
├── PROCESSORS/         # ❌ KHÔNG push (chạy local để tính toán)
│   └── ... (logic tính toán)
│
└── DATA/               # ❌ KHÔNG push (dữ liệu local)
    ├── raw/            # Dữ liệu thô
    └── processed/      # Kết quả đã xử lý (có thể push riêng nếu cần)
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
# 1. Tính toán data (local)
python PROCESSORS/pipelines/daily_update.py

# 2. Chạy Streamlit (local)
streamlit run WEBAPP/main.py
```

### Production (Streamlit Cloud)
```bash
# 1. Code tự động deploy từ GitHub
# 2. Streamlit đọc data từ external source
# 3. Hiển thị dashboard
```

---

## 🎯 NOTES

- **Repository này chỉ để deploy Streamlit**, không chứa processing logic
- **Processing logic** chạy local để tạo parquet files
- **Parquet files** có thể upload riêng hoặc lưu external storage
- **Streamlit** chỉ đọc và hiển thị, không tính toán

---

**Last Updated:** 2025-12-08  
**Status:** ✅ Optimized for Streamlit Cloud deployment