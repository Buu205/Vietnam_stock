import os
import logging
from typing import List
import numpy as np
import pandas as pd
import sys

# Add core module to path for date formatter
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from date_formatter import DateFormatter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankFinancialCalculator:
	"""Compute bank financial metrics from processed fundamental data.
	Tính toán các chỉ số tài chính ngân hàng từ dữ liệu cơ bản đã xử lý.

	Units / Đơn vị:
	- Components/Growth: Billion VND (VND / 1e9) / Tỷ đồng (VND / 1e9)
	- Profitability, Efficiency, Liquidity/Capital adequacy: Percentage (%) / Phần trăm (%)
	- Valuation (BVPS, EPS): VND per share / VND mỗi cổ phiếu

	Metric Codes Mapping / Bảng tra cứu mã chỉ số (from bank_metrics_lookup.json - code = original_name):
	- BIS_1: Thu nhập lãi và các khoản thu nhập tương tự
	- BIS_2: Chi phí lãi và các chi phí tương tự
	- BIS_3: Thu nhập lãi thuần
	- BIS_14: Chi phí hoạt động
	- BIS_14A: Tổng thu nhập hoạt động
	- BIS_15: Lợi nhuận thuần từ hoạt động kinh doanh trước chi phí dự phòng rủi ro tín dụng
	- BIS_16: Chi phí dự phòng rủi ro tín dụng
	- BIS_17: Tổng lợi nhuận trước thuế
	- BIS_22A: Cổ đông của Công ty mẹ
	- BBS_100: Tài sản
	- BBS_120: Tiền gửi tại NHNN
	- BBS_130: Tiền, vàng gửi tại các TCTD khác và cho vay các TCTD khác
	- BBS_140: Chứng khoán kinh doanh
	- BBS_160: Cho vay khách hàng
	- BBS_170: Chứng khoán đầu tư
	- BBS_180: Hoạt động mua nợ
	- BBS_320: Tiền gửi và vay các TCTD khác
	- BBS_321: Tiền gửi của các TCTD khác
	- BBS_322: Vay các TCTD khác
	- BBS_330: Tiền gửi của khách hàng
	- BBS_340: Các công cụ tài chính phát sinh và các khoản nợ tài chính khác
	- BBS_360: Phát hành giấy tờ có giá
	- BBS_370: Các khoản nợ khác
	- BBS_500: Vốn của TCTD
	- BBS_411: Vốn điều lệ
	- BBS_7001: Lợi ích của cổ đông thiểu số (trước 2015)
	- BBS_161: Cho vay khách hàng
	- BBS_169: Dự phòng rủi ro cho vay khách hàng
	- BBS_181: Mua nợ
	- BNOT_4: Cho vay các TCTD khác phân theo chất lượng nợ vay
	- BNOT_4_2: Nợ cần chú ý
	- BNOT_4_3: Nợ dưới tiêu chuẩn
	- BNOT_4_4: Nợ nghi ngờ
	- BNOT_4_5: Nợ xấu có khả năng mất vốn
	- BNOT_5_1_3: Trái phiếu do các TCKT trong nước phát hành
	- BNOT_7_5: Cho vay bằng vốn tài trợ, ủy thác đầu tư
	- BNOT_13_1_1_3: Trái phiếu do các TCKT trong nước phát hành
	- BNOT_13_2_3: Trái phiếu do các TCKT trong nước phát hành
	- BNOT_26: Tiền gửi của khách hàng phân theo loại tiền gửi
	- BNOT_26_1: Tiền gửi không kỳ hạn
	- BNOT_26_3: Tiền gửi vốn chuyên dùng
	- BNOT_26_5: Tiền gửi ký quỹ
	- BNOT_31_1: Thu nhập lãi tiền gửi
	"""

	def __init__(self, data_path: str):
		self.data_path = data_path
		self.df: pd.DataFrame | None = None
		self.results: pd.DataFrame | None = None
		self.date_formatter = DateFormatter()

	def load_data(self) -> pd.DataFrame:
		logger.info(f"Loading data from {self.data_path}")
		self.df = pd.read_parquet(self.data_path)
		return self.df

	def pivot_data(self) -> pd.DataFrame:
		if self.df is None:
			self.load_data()
		
		# Chỉ sử dụng dữ liệu theo quý để tránh trộn với yearly/semi
		quarterly_df = self.df[self.df['FREQ_CODE'] == 'Q'].copy()
		
		pivot = quarterly_df.pivot_table(
			index=["SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE"],
			columns="METRIC_CODE",
			values="METRIC_VALUE",
			aggfunc="first",
		).reset_index()
		pivot.columns.name = None
		return pivot

	@staticmethod
	def _avg_two_quarters(series: pd.Series) -> pd.Series:
		return series.rolling(window=2, min_periods=1).mean()

	def compute_components(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute basic bank components (units: billion VND)
		Tính toán các thành phần cơ bản của ngân hàng (đơn vị: tỷ đồng)"""
		res = df.copy()
		
		# Basic components (Billion VND - VND / 1e9) / Các thành phần cơ bản (Tỷ đồng - VND / 1e9)
		res["npl_amount"] = (res.get("BNOT_4_3", 0) + res.get("BNOT_4_4", 0) + res.get("BNOT_4_5", 0)) / 1e9  # NPL amount / Nợ xấu
		res["nii"] = res.get("BIS_3", 0) / 1e9  # Net interest income / Thu nhập lãi thuần
		res["toi"] = res.get("BIS_14A", 0) / 1e9  # Total operating income / Tổng thu nhập hoạt động
		res["noii"] = res["toi"] - res["nii"]  # Non-operating interest income / Thu nhập phi lãi
		res["opex"] = res.get("BIS_14", 0) / 1e9  # Operating expenses / Chi phí hoạt động
		res["ppop"] = res.get("BIS_15", 0) / 1e9  # Pre-provision operating profit / Lợi nhuận trước dự phòng
		res["provision_expense"] = res.get("BIS_16", 0) / 1e9  # Provision expense / Chi phí dự phòng
		res["pbt"] = res.get("BIS_17", 0) / 1e9  # Profit before tax / Lợi nhuận trước thuế
		res["npatmi"] = res.get("BIS_22A", 0) / 1e9  # Net profit after tax and minority interest / Lợi nhuận sau thuế
		res["interest_income"] = res.get("BIS_1", 0) / 1e9  # Interest income / Thu nhập lãi
		res["interest_expense"] = res.get("BIS_2", 0) / 1e9  # Interest expense / Chi phí lãi
		
		# Interest earning assets and Interest bearing liabilities (Billion VND) / Tài sản sinh lãi và Nợ phải trả có lãi (Tỷ đồng)
		res["iea"] = (
			res.get("BBS_120", 0)  # Cash and cash equivalents / Tiền và tương đương tiền
			+ res.get("BBS_130", 0)  # Receivables / Các khoản phải thu
			+ res.get("BBS_140", 0)  # Financial investments / Các khoản đầu tư tài chính
			+ res.get("BBS_160", 0)  # Customer loans / Cho vay khách hàng
			+ res.get("BBS_170", 0)  # Other investments / Các khoản đầu tư khác
			+ res.get("BBS_180", 0)  # Fixed assets / Tài sản cố định
		) / 1e9
		res["ibl"] = (
			res.get("BBS_320", 0)  # Short-term liabilities / Nợ phải trả ngắn hạn
			+ res.get("BBS_321", 0)  # Long-term liabilities / Nợ phải trả dài hạn
			+ res.get("BBS_330", 0)  # Customer deposits / Tiền gửi khách hàng
			+ res.get("BBS_360", 0)  # Other liabilities / Nợ phải trả khác
			+ res.get("BBS_370", 0)  # Equity / Vốn chủ sở hữu
		) / 1e9
		
		# 2-quarter averages (by bank) / Trung bình 2 quý (theo từng ngân hàng)
		res = res.sort_values(["SECURITY_CODE", "REPORT_DATE"])  # ensure order / đảm bảo thứ tự
		res["avg_iea_2q"] = res.groupby("SECURITY_CODE")["iea"].transform(self._avg_two_quarters)
		res["avg_ibl_2q"] = res.groupby("SECURITY_CODE")["ibl"].transform(self._avg_two_quarters)
		return res

	def compute_growth(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute growth metrics (units: billion VND)
		Tính toán các chỉ số tăng trưởng (đơn vị: tỷ đồng)"""
		res = df.copy()
		# Growth levels (Billion VND - VND / 1e9) / Các mức tăng trưởng (Tỷ đồng - VND / 1e9)
		# Handle NaN values by filling with 0 for missing components / Xử lý NaN bằng cách thay thế bằng 0
		res["total_credit"] = (
			res.get("BBS_161", 0).fillna(0)  # Customer loans / Cho vay khách hàng
			+ res.get("BBS_181", 0).fillna(0)  # Other credit / Tín dụng khác
			+ res.get("BNOT_5_1_3", 0).fillna(0)  # Other credit / Tín dụng khác
			+ res.get("BNOT_13_1_1_3", 0).fillna(0)  # Special credit / Tín dụng đặc biệt
			+ res.get("BNOT_13_2_3", 0).fillna(0)  # Other credit / Tín dụng khác
		) / 1e9
		res["customer_loan"] = res.get("BBS_161", 0) / 1e9  # Customer loans / Cho vay khách hàng
		res["customer_deposit"] = res.get("BBS_330", 0) / 1e9  # Customer deposits / Tiền gửi khách hàng
		return res

	def compute_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute profitability ratios (units: %)
		Tính toán các chỉ số sinh lời (đơn vị: %)"""
		res = df.copy()
		
		# TTM cho BIS_22A (Lợi nhuận sau thuế thuộc cổ đông Cty mẹ) - chuyển đổi sang tỷ đồng
		res = res.sort_values(["SECURITY_CODE", "REPORT_DATE"])  # đảm bảo thứ tự
		res["bis22a_ttm"] = (
			res.groupby("SECURITY_CODE")["BIS_22A"].transform(lambda s: s.rolling(window=4, min_periods=1).sum()) / 1e9
		)
		
		# Trung bình 2 quý liên tiếp của vốn chủ sở hữu và tài sản (chuyển đổi sang tỷ đồng)
		# Average of 2 consecutive quarters for equity and assets (unit: billion VND)
		# Equity average based on BBS_500 as requested; fill forward missing to avoid gaps per quarter
		res = res.sort_values(["SECURITY_CODE", "REPORT_DATE"])  # đảm bảo thứ tự trước khi ffill/rolling
		res["BBS_500_ffill"] = res.groupby("SECURITY_CODE")["BBS_500"].ffill()
		res["equity_avg_2q"] = (
			res.groupby("SECURITY_CODE")["BBS_500_ffill"].transform(lambda s: s.rolling(window=2, min_periods=1).mean())
			/ 1e9
		)
		res["assets_avg_2q"] = (
			res.groupby("SECURITY_CODE")["BBS_100"].transform(lambda s: s.rolling(window=2, min_periods=2).mean())
			/ 1e9
		)
		
		# ROEA (TTM) và ROAA (TTM) tính bằng % với tử số là BIS_22A (NPATMI) TTM
		res["roea_ttm"] = np.where(
			res["equity_avg_2q"] != 0,
			(res["bis22a_ttm"] / res["equity_avg_2q"]) * 100,
			np.nan,
		)
		res["roaa_ttm"] = np.where(
			res["assets_avg_2q"] != 0,
			(res["bis22a_ttm"] / res["assets_avg_2q"]) * 100,
			np.nan,
		)
		
		# Lợi suất tài sản, Chi phí huy động, NIM (quý %) sử dụng mẫu số trung bình 2Q
		# Chuyển đổi tử số sang tỷ đồng để nhất quán
		res["asset_yield_q"] = np.where(
			res["avg_iea_2q"] != 0,
			(res["BIS_1"] / 1e9 / res["avg_iea_2q"]) * 100,
			np.nan,
		)
		res["funding_cost_q"] = np.where(
			res["avg_ibl_2q"] != 0,
			(res["BIS_2"] / 1e9 / res["avg_ibl_2q"]) * 100,
			np.nan,
		)
		res["nim_q"] = np.where(
			res["avg_iea_2q"] != 0,
			(res["BIS_3"] / 1e9 / res["avg_iea_2q"]) * 100,
			np.nan,
		)
		
		# Lợi suất cho vay (Q) = BNOT_31_1 / (BBS_160 + BBS_180), mẫu số trung bình 2Q
		res["loan_base"] = (res.get("BBS_160", 0) + res.get("BBS_180", 0)) / 1e9  # Chuyển đổi sang tỷ đồng
		res = res.sort_values(["SECURITY_CODE", "REPORT_DATE"])  # đảm bảo thứ tự trước khi rolling
		res["loan_base_avg_2q"] = res.groupby("SECURITY_CODE")["loan_base"].transform(self._avg_two_quarters)
		res["loan_yield_q"] = np.where(
			res["loan_base_avg_2q"] != 0,
			(res.get("BNOT_31_1", 0) / 1e9 / res["loan_base_avg_2q"]) * 100,
			np.nan,
		)
		return res

	def compute_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute efficiency ratios (units: %)
		Tính toán các chỉ số hiệu quả (đơn vị: %)"""
		res = df.copy()
		
		# Tỷ lệ CASA = (Tiền gửi không kỳ hạn + Tiết kiệm + Có kỳ hạn) / Tổng tiền gửi
		casa_num = res.get("BNOT_26_1", 0) + res.get("BNOT_26_5", 0) + res.get("BNOT_26_3", 0)
		casa_den = res.get("BNOT_26", 0)
		res["casa_ratio"] = np.where(casa_den != 0, (casa_num / casa_den) * 100, np.nan)
		
		# Tỷ lệ chi phí/doanh thu = Chi phí hoạt động / Tổng thu nhập hoạt động
		res["cir"] = np.where(res.get("BIS_14A", 0) != 0, (res.get("BIS_14", 0) / res.get("BIS_14A", 0)) * 100, np.nan)
		
		# Tỷ lệ NII/TOI và NOII/TOI
		res["nii_toi"] = np.where(res["toi"] != 0, (res["nii"] / res["toi"]) * 100, np.nan)
		res["noii_toi"] = np.where(res["toi"] != 0, (1 - (res["nii"] / res["toi"])) * 100, np.nan)
		return res

	def compute_liquidity_and_capital(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute liquidity and capital adequacy ratios (units: %)
		Tính toán các chỉ số thanh khoản và vốn (đơn vị: %)"""
		res = df.copy()
		
		# LDR thuần = Cho vay khách hàng / (Tiền gửi khách hàng + Vốn chủ sở hữu)
		res["ldr_pure"] = np.where(
			(res.get("BBS_330", 0) + res.get("BBS_370", 0)) != 0,
			(res.get("BBS_161", 0) / (res.get("BBS_330", 0) + res.get("BBS_370", 0))) * 100,
			np.nan,
		)
		
		# LDR theo quy định (ước tính) = (Cho vay - Dự phòng) / (Vay ngắn hạn + Tiền gửi - Tiết kiệm - Có kỳ hạn + Vốn chủ sở hữu)
		reg_den = res.get("BBS_322", 0) + res.get("BBS_330", 0) - res.get("BNOT_26_5", 0) - res.get("BNOT_26_3", 0) + res.get("BBS_370", 0)
		res["ldr_regulated_estimated"] = np.where(reg_den != 0, ((res.get("BBS_161", 0) - res.get("BNOT_7_5", 0)) / reg_den) * 100, np.nan)
		
		# Tỷ lệ nợ nhóm 2 = Dư nợ nhóm 2 / Tổng dư nợ
		res["debt_group2_ratio"] = np.where(res.get("BNOT_4", 0) != 0, (res.get("BNOT_4_2", 0) / res.get("BNOT_4", 0)) * 100, np.nan)
		
		# Tỷ lệ nợ xấu = (Dư nợ nhóm 3 + 4 + 5) / Tổng dư nợ
		npl_num = res.get("BNOT_4_3", 0) + res.get("BNOT_4_4", 0) + res.get("BNOT_4_5", 0)
		res["npl_ratio"] = np.where(res.get("BNOT_4", 0) != 0, (npl_num / res.get("BNOT_4", 0)) * 100, np.nan)
		
		# Tỷ lệ nhóm 2-5 = (Dư nợ nhóm 2 + 3 + 4 + 5) / Tổng dư nợ
		grp_2_5 = res.get("BNOT_4_2", 0) + res.get("BNOT_4_3", 0) + res.get("BNOT_4_4", 0) + res.get("BNOT_4_5", 0)
		res["group2_to_total_ratio"] = np.where(res.get("BNOT_4", 0) != 0, (grp_2_5 / res.get("BNOT_4", 0)) * 100, np.nan)
		
		# Tỷ lệ dự phòng rủi ro = Dự phòng rủi ro tín dụng / (Dư nợ nhóm 3 + 4 + 5)
		res["llcr"] = np.where(npl_num != 0, (res.get("BBS_169", 0) / npl_num) * 100, np.nan)
		
		# Tổng dự phòng / Nợ nhóm 2-5 -> thiếu mã dự phòng (@28:28). Để NaN.
		res["total_provision_over_group2to5"] = np.nan
		return res

	def compute_valuation(self, df: pd.DataFrame) -> pd.DataFrame:
		"""Compute valuation metrics (units: VND per share)
		Tính toán các chỉ số định giá (đơn vị: VND mỗi cổ phiếu)"""
		res = df.copy()
		
		# Giá trị sổ sách mỗi cổ phiếu = (Vốn chủ sở hữu - Lợi ích cổ đông thiểu số) / (BBS_411 / 10,000)
		# BVPS = (BBS_410 - BBS_7001) / BBS_411, trong đó BBS_411/10,000 và BBS_410-BBS_7001 đơn vị VND
		equity = res.get("BBS_410", 0)  # Vốn chủ sở hữu (VND)
		minority_interest = res.get("BBS_7001", 0) if "BBS_7001" in res.columns else 0  # Lợi ích cổ đông thiểu số (VND)
		shares = res.get("BBS_411", 0) / 10000  # BBS_411 chia cho 10,000
		# Handle zero shares by setting BVPS to NaN / Xử lý số cổ phiếu = 0 bằng cách đặt BVPS = NaN
		res["bvps"] = np.where((shares > 0), (equity - minority_interest) / shares, np.nan)
		
		# Lợi nhuận mỗi cổ phiếu (TTM) = (Lợi nhuận sau thuế TTM / Số cổ phiếu) * 10
		res = res.sort_values(["SECURITY_CODE", "REPORT_DATE"])  # đảm bảo thứ tự
		res["bis22a_ttm"] = res.groupby("SECURITY_CODE")["BIS_22A"].transform(lambda s: s.rolling(window=4, min_periods=1).sum()) / 1e9
		# EPS (VND/share) = BIS_22A_TTM (billion VND) * 1e9 / shares
		# Xử lý shares = 0 bằng cách đặt EPS = NaN
		res["eps_ttm"] = np.where((shares > 0), (res["bis22a_ttm"] * 1e9) / shares, np.nan)
		return res

	def optimize_output(self, df: pd.DataFrame) -> pd.DataFrame:
		cols: List[str] = [
			# id
			"SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE",
			# components
			"npl_amount", "nii", "toi", "noii", "opex", "ppop", "provision_expense", "pbt", "npatmi",
			"interest_income", "interest_expense", "iea", "ibl", "avg_iea_2q", "avg_ibl_2q", "equity_avg_2q",
			# growth levels
			"total_credit", "customer_loan", "customer_deposit",
			# profitability
			"roea_ttm", "roaa_ttm", "asset_yield_q", "funding_cost_q", "nim_q", "loan_yield_q",
			# efficiency
			"casa_ratio", "cir", "nii_toi", "noii_toi",
			# liquidity/capital
			"ldr_pure", "ldr_regulated_estimated", "debt_group2_ratio", "npl_ratio", "group2_to_total_ratio", "llcr",
			# valuation
			"bvps", "eps_ttm",
		]
		available = [c for c in cols if c in df.columns]
		out = df[available].copy()
		# Rename to english readable
		rename = {
			"SECURITY_CODE": "symbol",
			"REPORT_DATE": "report_date",
			"YEAR": "year",
			"QUARTER": "quarter",
			"FREQ_CODE": "freq_code",
		}
		out = out.rename(columns=rename)
		return out

	def calculate_all(self) -> pd.DataFrame:
		pivot = self.pivot_data()
		logger.info(f"Pivoted: {pivot.shape}")
		c1 = self.compute_components(pivot)
		c2 = self.compute_growth(c1)
		c3 = self.compute_profitability(c2)
		c4 = self.compute_efficiency(c3)
		c5 = self.compute_liquidity_and_capital(c4)
		c6 = self.compute_valuation(c5)
		optimized = self.optimize_output(c6)
		
		# Chuẩn hóa date format trước khi return
		logger.info("Standardizing date format to YYYY-MM-DD...")
		optimized = self.date_formatter.standardize_all_date_columns(optimized, inplace=True)
		
		self.results = optimized
		logger.info(f"Computed: {optimized.shape}")
		logger.info(f"Date format sample: {optimized['report_date'].head(3).tolist() if 'report_date' in optimized.columns else 'No report_date column'}")
		return optimized

	def save(self, output_path: str) -> None:
		if self.results is None:
			raise ValueError("No results to save. Run calculate_all() first.")
		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		self.results.to_parquet(output_path, index=False)
		logger.info(f"Saved to {output_path}")


def main():
	"""Main function to run bank financial metrics calculation
	Hàm chính để chạy tính toán các chỉ số tài chính ngân hàng"""
	# Xác định PROJECT_ROOT
	from pathlib import Path
	current_file = Path(__file__).resolve()
	project_root = current_file.parent.parent.parent
	
	data_path = f"{project_root}/data_warehouse/raw/fundamental/processed/bank_full.parquet"
	output_path = f"{project_root}/calculated_results/fundamental/bank/bank_financial_metrics.parquet"
	
	# Tạo calculator và tính toán
	calc = BankFinancialCalculator(data_path)
	calc.calculate_all()
	calc.save(output_path)
	print("Hoàn thành tính toán các chỉ số tài chính ngân hàng!")


if __name__ == "__main__":
	main()
