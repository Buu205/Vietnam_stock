# Chiến thuật Giao dịch: Buy Pullback (Khung 4-8 Tuần)

## 1. Tổng quan Chiến thuật
* **Khung thời gian:** 4-8 Tuần (Medium Swing / Trend Following).
* **Triết lý:** "Đi theo bóng lớn" (Follow the Trend). Chỉ mua khi xu hướng trung hạn Tăng, nhưng mua ở nhịp chỉnh ngắn hạn (Pullback) để có giá vốn tốt.
* **Nguyên tắc cốt lõi:**
    * **Loại bỏ MA200:** Quá chậm cho khung này.
    * **Tập trung MA50:** Là đường "sinh mệnh" xác định xu hướng.
    * **Dùng MA100:** Là "bộ lọc an toàn" (Regime Filter).
    * **Dùng MA20:** Là "cò súng" (Trigger) để tìm điểm vào lệnh.

---

## 2. Cơ cấu Trọng số (Weighting)
Dùng để tính **Market Health Score** (Điểm sức khỏe thị trường) nhằm có cái nhìn tổng quan nhanh.

| Chỉ báo Breadth | Trọng số | Vai trò |
| :--- | :--- | :--- |
| **MA50** | **50%** | **Xương sống (Trend):** Quyết định xu hướng chính. |
| **MA20** | **30%** | **Timing (Momentum):** Đo độ nóng lạnh ngắn hạn. |
| **MA100** | **20%** | **Nền tảng (Safety):** Xác nhận bối cảnh dài hơi hơn. |

---

## 3. Logic Code Python

### Phần A: Logic Cơ bản (Tính điểm)
Mục đích: Đánh giá trạng thái chung (Xanh/Đỏ/Vàng) để quyết định tâm thế giao dịch.

```python
# Giả định: state.breadth_maXX_pct là dữ liệu % cổ phiếu nằm trên MA tương ứng

# 1. Cấu hình trọng số
w_ma50 = 0.5
w_ma20 = 0.3
w_ma100 = 0.2

# 2. Tính điểm Composite (Market Score)
market_score = (state.breadth_ma50_pct * w_ma50) + \
               (state.breadth_ma20_pct * w_ma20) + \
               (state.breadth_ma100_pct * w_ma100)

# 3. Phân loại trạng thái sơ bộ
if market_score > 75:
    status_text = "Thị trường Tăng mạnh (Strong Uptrend)"
    status_color = "#10B981" # Xanh
elif market_score < 30:
    status_text = "Thị trường Yếu (Weak/Downtrend)"
    status_color = "#EF4444" # Đỏ
else:
    status_text = "Thị trường Phân hóa / Tích lũy"
    status_color = "#F59E0B" # Cam



    # Lấy dữ liệu đầu vào
b_ma20 = state.breadth_ma20_pct
b_ma50 = state.breadth_ma50_pct
b_ma100 = state.breadth_ma100_pct

# --- BƯỚC 1: ĐỊNH NGHĨA TRẠNG THÁI ---

# Trend Filter: Trend khỏe khi cả trung hạn (MA50) và nền tảng (MA100) đều > 50%
is_uptrend = (b_ma50 >= 50) and (b_ma100 >= 50)

# Oscillator: Đo độ quá mua/quá bán ngắn hạn bằng MA20
is_oversold_short_term = b_ma20 < 40  # Vùng mua tiêu chuẩn
is_extreme_oversold = b_ma20 < 20     # Vùng mua hoảng loạn (Deep value)
is_overbought = b_ma20 > 80           # Vùng hưng phấn
is_recovering = b_ma20 > state.prev_breadth_ma20_pct # (Tùy chọn): Đã bắt đầu ngóc đầu lên

# --- BƯỚC 2: RA TÍN HIỆU (SIGNAL MATRIX) ---

signal_msg = ""
recommendation = ""
signal_color = ""

if is_uptrend:
    # === KỊCH BẢN UPTREND (Canh Mua) ===
    
    if is_extreme_oversold:
        # Cơ hội tốt nhất: Trend tăng nhưng ngắn hạn bị bán tháo quá đà
        signal_msg = "💎 DIAMOND BUY: Deep Pullback"
        recommendation = "Giải ngân mạnh. Rũ bỏ hoàn hảo."
        signal_color = "#059669" # Xanh đậm
        
    elif is_oversold_short_term:
        # Cơ hội tiêu chuẩn: Nhịp chỉnh thông thường
        signal_msg = "✅ STANDARD BUY: Normal Pullback"
        recommendation = "Mua gia tăng hoặc Mở vị thế mới."
        signal_color = "#10B981" # Xanh lá
        
    elif is_overbought:
        # Rủi ro ngắn hạn
        signal_msg = "⚠️ WARNING: Overheated"
        recommendation = "Không mua đuổi. Canh chốt lời margin."
        signal_color = "#F59E0B" # Cam
        
    else:
        # Trạng thái bình thường
        signal_msg = "⚓ HOLD: Riding the Trend"
        recommendation = "Nắm giữ danh mục. Trend vẫn tốt."
        signal_color = "#3B82F6" # Xanh dương

else: 
    # === KỊCH BẢN DOWNTREND / SIDEWAYS (Canh Bán/Thủ) ===
    # (Khi b_ma50 < 50 hoặc b_ma100 < 50)
    
    if b_ma20 > 70:
        # Hồi quang phản chiếu
        signal_msg = "⛔ SELL: Bull Trap"
        recommendation = "Bán hạ tỷ trọng ngay. Đây là bẫy tăng giá."
        signal_color = "#DC2626" # Đỏ đậm
        
    elif b_ma50 < 30 and b_ma20 < 20:
        # Sập gầm (Crash)
        signal_msg = "☠️ DANGER: Market Crash"
        recommendation = "Đứng ngoài tuyệt đối. Tuyệt đối không bắt đáy sớm."
        signal_color = "#7F1D1D" # Đỏ thẫm
        
    else:
        signal_msg = "💤 WAIT: No Trend"
        recommendation = "Quan sát. Chưa có điểm vào an toàn."
        signal_color = "#9CA3AF" # Xám


        Hướng dẫn Hành động (Action Plan)
Khi thấy "DIAMOND BUY" hoặc "STANDARD BUY":

Kiểm tra danh mục theo dõi (Watchlist).

Chọn các cổ phiếu vẫn giữ được MA50 trong khi thị trường chỉnh.

Giải ngân 30-50% sức mua.

Khi thấy "WARNING: Overheated":

Dừng mua mới.

Siết chặt lệnh Stoploss (Trailing Stop) lên gần giá hiện tại.

Khi thấy "SELL: Bull Trap" hoặc "DANGER":

Ưu tiên GIỮ TIỀN.

Nếu đang kẹp hàng, canh các nhịp hồi trong phiên để thoát.