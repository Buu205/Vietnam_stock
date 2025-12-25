Chào bạn, tôi sẽ đi thẳng vào công thức toán học cụ thể (Mathematical Formulas) để bạn có thể đưa vào code ngay lập tức.

Tùy vào mục đích sử dụng (Vẽ biểu đồ hay Lọc cổ phiếu), chúng ta có 2 công thức chuẩn mực nhất thế giới hiện nay:

1. Công thức vẽ Chart (Stan Weinstein / Mansfield RS)
Đây là công thức để vẽ đường RS Line chạy bên dưới giá mà bạn thường thấy trong sách phương Tây. Nó giúp bạn nhìn thấy xu hướng sức mạnh.

Bước 1: Tính Tỷ lệ cơ sở (Base Ratio)
So sánh giá đóng cửa của Cổ phiếu (hoặc Ngành) với VN-Index tại ngày t:

Ratio 
t
​
 = 
Index_Value 
t
​
 
Close_Price 
t
​
 
​
 
Bước 2: Tính Trung bình trượt của Tỷ lệ (Moving Average of Ratio)
Chuẩn mực của Weinstein là dùng đường trung bình 52 tuần (tương đương 52 phiên tuần hoặc ~260 phiên ngày).

Avg_Ratio 
t
​
 =SMA(Ratio,52)
Bước 3: Tính Mansfield Relative Strength (MRS)
Công thức này chuẩn hóa dữ liệu, biến đường RS dao động quanh mốc 0 (Zero Line).

Trên 0: Mạnh hơn thị trường.

Dưới 0: Yếu hơn thị trường.

MRS 
t
​
 =( 
Avg_Ratio 
t
​
 
Ratio 
t
​
 
​
 −1)×10
(Nhân 10 hoặc 100 để số hiển thị to hơn cho đẹp, không ảnh hưởng ý nghĩa).

2. Công thức chấm điểm Ranking (IBD Style)
Đây là công thức để ra con số RS Rating (1-99) dùng để lọc (Scan) cổ phiếu. Nó trả lời câu hỏi: "Cổ phiếu này mạnh hơn bao nhiêu % cổ phiếu khác?".

IBD (Investor's Business Daily) không công bố công thức độc quyền, nhưng giới Quant thế giới đã giải mã (Reverse Engineering) ra công thức xấp xỉ chính xác nhất (Weighted Alpha).

Bước 1: Tính hiệu suất có trọng số (Weighted Performance)
Chúng ta tính mức tăng giá (ROC - Rate of Change) của 4 quý gần nhất, nhưng gán trọng số cao nhất cho quý gần nhất.

Raw_Score=0.4×P 
3m
​
 +0.2×P 
6m
​
 +0.2×P 
9m
​
 +0.2×P 
12m
​
 
Trong đó:

P 
3m
​
 : % Thay đổi giá trong 3 tháng (1 Quý).

P 
6m
​
 : % Thay đổi giá trong 6 tháng (2 Quý).

...

Bước 2: Xếp hạng phần trăm (Percentile Ranking)
Đây là bước quan trọng nhất mà nhiều người bỏ quên. Con số Raw_Score ở trên không có ý nghĩa nếu đứng một mình. Bạn phải so sánh nó với toàn bộ thị trường (457 mã).

RS_Rating=PercentileRank(Raw_Score,All_Stocks)
Ví dụ: Nếu Raw_Score của HPG cao hơn 90% các mã khác trong database, thì RS Rating của HPG = 90.

3. Triển khai Code (Python / Pandas)
Dưới đây là đoạn code mẫu "Mì ăn liền" để bạn tính cả 2 loại trên:

Python

import pandas as pd
import numpy as np

def calculate_technical_rs(df_stock, df_index):
    """
    df_stock: DataFrame chứa cột 'Close' của cổ phiếu (index là datetime)
    df_index: DataFrame chứa cột 'Close' của VN-INDEX (index là datetime)
    """
    
    # --- PHẦN 1: MANSFIELD RS (ĐỂ VẼ CHART) ---
    
    # 1. Tính Ratio
    rs_ratio = df_stock['Close'] / df_index['Close']
    
    # 2. Tính SMA 52 tuần (Nếu data ngày thì dùng window=260, tuần thì window=52)
    # Giả sử data daily
    sma_ratio = rs_ratio.rolling(window=260).mean()
    
    # 3. Tính Mansfield RS
    mansfield_rs = ((rs_ratio / sma_ratio) - 1) * 10
    
    
    # --- PHẦN 2: IBD RS RATING (ĐỂ XẾP HẠNG) ---
    # Lưu ý: Phần này chỉ tính Raw Score cho 1 mã. 
    # Bạn cần chạy loop cho cả thị trường rồi mới Rank.
    
    # Tính % thay đổi cho các khung thời gian (giả sử 1 tháng = 21 phiên)
    roc_3m = df_stock['Close'].pct_change(periods=63)  # 3 tháng
    roc_6m = df_stock['Close'].pct_change(periods=126) # 6 tháng
    roc_9m = df_stock['Close'].pct_change(periods=189) # 9 tháng
    roc_12m = df_stock['Close'].pct_change(periods=252) # 12 tháng
    
    # Công thức trọng số (40% cho quý gần nhất)
    raw_rs_score = (0.4 * roc_3m) + (0.2 * roc_6m) + (0.2 * roc_9m) + (0.2 * roc_12m)
    
    return mansfield_rs, raw_rs_score

# --- PHẦN 3: LOGIC RANKING (SAU KHI CÓ RAW SCORE CỦA TOÀN THỊ TRƯỜNG) ---
def get_final_ranking(all_stocks_scores):
    """
    all_stocks_scores: Series chứa Raw Score của tất cả mã tại ngày T
    """
    # Dùng hàm rank của pandas để ra percentile (0 -> 1)
    # Nhân 99 để ra thang điểm 1-99 chuẩn IBD
    rs_rating = all_stocks_scores.rank(pct=True) * 99
    
    return rs_rating.round(0)
Tổng kết
Nếu bạn muốn nhìn xu hướng: Dùng công thức Mansfield.

Nếu bạn muốn lọc siêu cổ phiếu: Dùng công thức Weighted Alpha rồi Ranking 1-99.

Hệ thống của bạn nên có cả hai: Ranking để lọc ra List theo dõi, và Mansfield Chart để chọn điểm mua (khi đường Mansfield cắt lên đường Zero).