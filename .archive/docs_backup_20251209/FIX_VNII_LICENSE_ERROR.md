# 🛠️ SỬA LỖI XÁC THỰC VNII TRONG VNSTOCK

## Vấn đề

Khi chạy script `ohlcv_daily_updater.py` hoặc bất kỳ script nào sử dụng vnstock_data, bạn có thể gặp lỗi:
```
❌ Authentication failed: Network error during license verification: Expecting value: line 1 column 1 (char 0)
Please check your connection and try again.
```

Đây là lỗi xác thực với vnii (Vietnam Internet Infrastructure) khi vnstock cố gắng xác thực license.

## Giải pháp

### 1. Cập nhật vnstock và các packages liên quan

```bash
pip3 install -U vnstock vnstock_data vnstock_ta
```

### 2. Kiểm tra kết nối mạng

Đảm bảo bạn có kết nối internet ổn định và không bị firewall chặn các kết nối đến server của vnstock.

### 3. Cài đặt lại vnstock với installer chính thức

Đây là giải pháp hiệu quả nhất:

```bash
# Clone repository chứa installer
git clone https://github.com/vnstock-hq/vnstock_insider_guide

# Di chuyển đến thư mục installer
cd vnstock_insider_guide/oneclick_installer

# Dành cho macOS
chmod +x oneclick_python_vnstock3_macos.sh
./oneclick_python_vnstock3_macos.sh

# Nếu dùng Linux
chmod +x linux_installer.run
./linux_installer.run
```

Sau khi cài đặt lại, hãy khởi động lại terminal hoặc IDE.

### 4. Sử dụng source dữ liệu khác

Trong khi chờ sửa lỗi vnii, bạn có thể thay đổi source dữ liệu trong script:

```python
# Thay vì dùng 'vnd' (mặc định)
df = stock_historical_data(symbol='ACB', start='2024-01-01', end='2024-12-31', source='vnd')

# Thử dùng 'TCBS'
df = stock_historical_data(symbol='ACB', start='2024-01-01', end='2024-12-31', source='TCBS')
```

### 5. Sử dụng tài khoản thành viên tài trợ (nếu có)

Nếu bạn là thành viên tài trợ của vnstock, bạn có thể sử dụng API với rate limit cao hơn:

```python
from vnstock_data.explorer.vci import Quote

# Khởi tạo với nguồn VCI - dành riêng cho thành viên tài trợ
quote = Quote(symbol='ACB')

# Lấy dữ liệu với rate limit cao hơn
historical_data = quote.history(
    start='2000-07-28',
    end='2024-08-31',
    interval='1D'
)
```

### 6. Tạm thời bỏ qua xác thực (nếu chỉ cần demo)

Nếu bạn chỉ cần chạy script để test mà không cần dữ liệu thực, bạn có thể:

1. Sử dụng data mẫu có sẵn
2. Tạo mock data cho testing
3. Chạy script với flag `--dry-run` nếu có

## Phòng ngừa trong tương lai

1. **Giữ cho vnstock luôn được cập nhật**: Chạy `pip3 install -U vnstock` định kỳ
2. **Theo dõi thông báo**: Kiểm tra GitHub repository của vnstock để biết về các vấn đề và bản sửa lỗi
3. **Luôn có backup data**: Lưu trữ dữ liệu đã tải về để sử dụng khi API gặp sự cố

## Liên hệ hỗ trợ

Nếu các giải pháp trên không hiệu quả, hãy liên hệ:
- GitHub repository: https://github.com/vnstock-hq/vnstock
- Website chính thức: https://vnstocks.com/
- Cộng đồng: https://facebook.com/groups/vnstock.official