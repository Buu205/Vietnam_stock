# 🚀 CÁCH CHẠY SCRIPT CORRECTLY

## Vấn đề Import Error

Khi chạy script Python trực tiếp với `python3 script.py`, bạn có thể gặp lỗi `ModuleNotFoundError` vì Python không tìm thấy các module trong project của bạn.

## Giải pháp

### Method 1: Sử dụng PYTHONPATH (Recommended)

```bash
PYTHONPATH=/path/to/your/project python3 path/to/script.py
```

Ví dụ cụ thể:
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard /usr/local/bin/python3 /Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py
```

### Method 2: Chạy từ project root với -m flag

```bash
cd /path/to/your/project
python3 -m processors.technical.ohlcv.ohlcv_daily_updater
```

### Method 3: Tạo shell script wrapper

Tạo file `run_script.sh`:
```bash
#!/bin/bash
export PYTHONPATH=/path/to/your/project:$PYTHONPATH
python3 path/to/script.py "$@"
```

## Quick Reference cho các script chính

```bash
# OHLCV Daily Updater
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py

# Fundamental Calculators
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/fundamental/calculators/company_calculator.py
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/fundamental/calculators/bank_calculator.py
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/fundamental/calculators/insurance_calculator.py
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/fundamental/calculators/security_calculator.py
```

## Lưu ý quan trọng

1. Luôn sử dụng đường dẫn tuyệt đối với PYTHONPATH
2. Nếu script cần config file, đảm bảo chúng tồn tại
3. Một số script có thể cần xác thực API keys trước khi chạy