"""
Test: Đọc assumption từ file Excel OneDrive đã sync local.

File Excel: MWG_12.9.2022.xlsx
Sheet: READ_PYTHON
"""

import pandas as pd
import shutil
import os
from pathlib import Path

# --- CẤU HÌNH ---
SOURCE_FILE = Path(
    "/Users/buuphan/Library/CloudStorage/OneDrive-BIDVSecuritiesJSC/"
    "Equity Team/General/03. Sector Materials/"
    "3.4 Nhóm 4 (Tiêu dùng, XNK, Logistics)/Bán lẻ _Tiêu dùng/3.10.22/"
    "MWG_12.9.2022.xlsx"
)

TEMP_FILE = Path("/tmp/onedrive_assumption_temp.xlsx")
SHEET_NAME = "READ_PYTHON"


def read_assumption_from_onedrive():
    """
    Đọc dữ liệu assumption từ file Excel OneDrive.

    Returns:
        pd.DataFrame | None: DataFrame chứa dữ liệu, hoặc None nếu lỗi
    """
    # 1. KIỂM TRA FILE TỒN TẠI
    if not SOURCE_FILE.exists():
        print(f"❌ Lỗi: Không tìm thấy file tại:\n   {SOURCE_FILE}")
        print("\n💡 Kiểm tra:")
        print("   - OneDrive đã sync chưa?")
        print("   - Đường dẫn có đúng không?")
        return None

    print(f"✅ Tìm thấy file: {SOURCE_FILE.name}")
    print(f"   Size: {SOURCE_FILE.stat().st_size / 1024:.1f} KB")

    try:
        # 2. COPY RA FILE TẠM (Tránh xung đột OneDrive lock)
        shutil.copyfile(SOURCE_FILE, TEMP_FILE)
        print("✅ Đã copy file tạm thành công")

        # 3. ĐỌC SHEET READ_PYTHON
        df = pd.read_excel(TEMP_FILE, sheet_name=SHEET_NAME)
        print(f"✅ Đọc sheet '{SHEET_NAME}' thành công")
        print(f"   Shape: {df.shape[0]} rows x {df.shape[1]} columns")

        return df

    except ValueError as e:
        if "Worksheet" in str(e):
            print(f"❌ Không tìm thấy sheet '{SHEET_NAME}'")
            # Liệt kê các sheet có sẵn
            xl = pd.ExcelFile(TEMP_FILE)
            print(f"   Các sheet có sẵn: {xl.sheet_names}")
        else:
            print(f"❌ Lỗi đọc file: {e}")
        return None

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
        return None

    finally:
        # 4. DỌN DẸP FILE TẠM
        if TEMP_FILE.exists():
            os.remove(TEMP_FILE)
            print("🧹 Đã xóa file tạm")


def unpivot_assumption(df: pd.DataFrame, id_cols: list[str] = None) -> pd.DataFrame:
    """
    Xoay dọc (unpivot) dữ liệu assumption từ dạng ngang sang dọc.

    Args:
        df: DataFrame gốc (dạng ngang - các cột là ngày/quý)
        id_cols: Các cột giữ nguyên (mặc định tự detect)

    Returns:
        DataFrame đã xoay dọc
    """
    if df is None or df.empty:
        return None

    # Tự động detect id_cols nếu không truyền vào
    if id_cols is None:
        # Giả sử 2 cột đầu là metric_code, unit
        id_cols = df.columns[:2].tolist()

    df_long = pd.melt(
        df,
        id_vars=id_cols,
        var_name='period',
        value_name='value'
    )

    # Cố gắng parse period thành datetime
    df_long['period'] = pd.to_datetime(df_long['period'], errors='coerce')

    return df_long

import os

def save_to_parquet(df: pd.DataFrame, filename: str = "assumption_from_onedrive.parquet"):
    """
    Lưu DataFrame ra file parquet tại thư mục hiện tại của file này.
    """
    if df is None or df.empty:
        print("⚠️ Không có dữ liệu để lưu parquet.")
        return

    # Lấy thư mục hiện tại của file này
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(current_dir, filename)
    try:
        df.to_parquet(out_path, index=False)
        print(f"💾 Đã lưu file Parquet: {out_path}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu parquet: {e}")


# --- CHẠY THỬ ---
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Đọc Assumption từ OneDrive Excel")
    print("=" * 60)
    print()

    # Đọc dữ liệu
    df_result = read_assumption_from_onedrive()

    if df_result is not None:
        print()
        print("-" * 60)
        print("📊 THÔNG TIN DATAFRAME:")
        print("-" * 60)
        print(f"Columns: {list(df_result.columns)}")
        print()
        print("Dtypes:")
        print(df_result.dtypes)
        print()
        print("-" * 60)
        print("5 DÒNG ĐẦU TIÊN:")
        print("-" * 60)
        print(df_result.head())
        print()

        # Lưu ra parquet
        save_to_parquet(df_result)

        # Đọc lại parquet để verify
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parquet_path = os.path.join(current_dir, "assumption_from_onedrive.parquet")
        if os.path.exists(parquet_path):
            print()
            print("-" * 60)
            print("📂 VERIFY PARQUET FILE:")
            print("-" * 60)
            df_check = pd.read_parquet(parquet_path)
            print(f"Shape: {df_check.shape}")
            print(df_check.head())
    else:
        print("\n⚠️ Không đọc được dữ liệu!")
