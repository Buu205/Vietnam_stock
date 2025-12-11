#!/usr/bin/env python3
"""
Vietnamese Docstrings Updater - Cập nhật docstrings tiếng Việt
================================================================

Script này tự động cập nhật docstrings cho tất cả formulas
để đảm bảo consistency và có Vietnamese benchmarks.

Usage:
    python scripts/update_vietnamese_docstrings.py
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class VietnameseDocstringUpdater:
    """Update docstrings with Vietnamese content"""
    
    def __init__(self):
        self.formulas_dir = Path("PROCESSORS/fundamental/formulas")
        self.valuation_formulas_dir = Path("PROCESSORS/valuation/formulas")
        
        # Vietnamese benchmarks cho thị trường Việt Nam
        self.vietnam_benchmarks = {
            'roe': {
                'excellent': '> 20%',
                'good': '15-20%', 
                'acceptable': '10-15%',
                'poor': '< 10%'
            },
            'roa': {
                'excellent': '> 15%',
                'good': '10-15%',
                'acceptable': '5-10%', 
                'poor': '< 5%'
            },
            'gross_margin': {
                'manufacturing': '20-40%',
                'retail': '15-30%',
                'services': '30-50%',
                'tech': '50-70%'
            },
            'net_margin': {
                'excellent': '> 15%',
                'good': '10-15%',
                'acceptable': '5-10%',
                'poor': '< 5%'
            },
            'current_ratio': {
                'strong': '> 2.0',
                'good': '1.5-2.0',
                'acceptable': '1.0-1.5',
                'concern': '< 1.0'
            },
            'debt_to_equity': {
                'conservative': '< 0.5',
                'moderate': '0.5-1.0',
                'aggressive': '1.0-2.0',
                'high_risk': '> 2.0'
            },
            'asset_turnover': {
                'high': '> 2.0',
                'good': '1.0-2.0',
                'low': '< 1.0'
            },
            'inventory_turnover': {
                'high': '> 12',
                'good': '6-12',
                'low': '< 6'
            }
        }
    
    def extract_function_info(self, file_path: Path) -> List[Tuple[str, str, int, int]]:
        """
        Extract function information from Python file
        
        Returns:
            List of (function_name, source_code, start_line, end_line)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            return []
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('calculate_'):
                    # Extract source code
                    start_line = node.lineno - 1
                    end_line = node.end_lineno
                    lines = content.split('\n')
                    source_code = '\n'.join(lines[start_line:end_line])
                    
                    functions.append((node.name, source_code, start_line, end_line))
        
        return functions
    
    def generate_vietnamese_docstring(self, func_name: str, existing_docstring: str = "") -> str:
        """
        Generate Vietnamese docstring based on function name
        """
        # Extract base name from function name
        base_name = func_name.replace('calculate_', '')
        
        # Map function names to Vietnamese descriptions
        formula_descriptions = {
            'roe': 'Tỷ suất sinh lời trên vốn chủ sở hữu (Return on Equity)',
            'roa': 'Tỷ suất sinh lời trên tổng tài sản (Return on Assets)',
            'gross_margin': 'Biên lợi nhuận gộp (Gross Profit Margin)',
            'net_margin': 'Biên lợi nhuận ròng (Net Profit Margin)',
            'operating_margin': 'Biên lợi nhuận hoạt động (Operating Margin)',
            'current_ratio': 'Tỷ lệ thanh toán hiện hành (Current Ratio)',
            'debt_to_equity': 'Tỷ lệ nợ trên vốn chủ sở hữu (Debt to Equity)',
            'asset_turnover': 'Tỷ lệ quay vòng tổng tài sản (Asset Turnover)',
            'inventory_turnover': 'Tỷ lệ quay vòng hàng tồn kho (Inventory Turnover)',
            'eps': 'Lợi nhuận trên mỗi cổ phiếu (Earnings Per Share)',
            'yoy_growth': 'Tốc độ tăng trưởng năm so với năm (Year-over-Year Growth)',
            'qoq_growth': 'Tốc độ tăng trưởng quý so với quý (Quarter-over-Quarter Growth)',
            'ttm_sum': 'Tổng 12 tháng gần nhất (Trailing Twelve Months Sum)',
            'ttm_avg': 'Trung bình 12 tháng gần nhất (Trailing Twelve Months Average)',
            'receivables_turnover': 'Tỷ lệ quay vòng các khoản phải thu (Receivables Turnover)',
            'payables_turnover': 'Tỷ lệ quay vòng các khoản phải trả (Payables Turnover)',
            'revenue_growth': 'Tốc độ tăng trưởng doanh thu (Revenue Growth)',
            'profit_growth': 'Tốc độ tăng trưởng lợi nhuận (Profit Growth)',
            'free_cash_flow': 'Dòng tiền tự do (Free Cash Flow)'
        }
        
        # Get description
        description = formula_descriptions.get(base_name, f'Financial metric: {base_name}')
        
        # Generate formula based on function name
        formula = self._generate_formula(base_name)
        
        # Generate interpretation based on benchmarks
        interpretation = self._generate_interpretation(base_name)
        
        # Generate examples
        examples = self._generate_examples(base_name)
        
        # Build complete docstring
        docstring = f'''    """
    {description}

    Công thức: {formula}

    Đo lường: {self._generate_measurement(base_name)}

    Diễn giải:
{interpretation}

    Args:
        {self._generate_args(base_name)}

    Returns:
        {self._generate_returns(base_name)}

    Examples:
{examples}
    """'''
        
        return docstring
    
    def _generate_formula(self, base_name: str) -> str:
        """Generate formula string"""
        formulas = {
            'roe': '(Lợi nhuận sau thuế / Vốn chủ sở hữu) × 100',
            'roa': '(Lợi nhuận sau thuế / Tổng tài sản) × 100',
            'gross_margin': '(Lợi nhuận gộp / Doanh thu) × 100',
            'net_margin': '(Lợi nhuận ròng / Doanh thu) × 100',
            'operating_margin': '(Lợi nhuận hoạt động / Doanh thu) × 100',
            'current_ratio': 'Tài sản ngắn hạn / Nợ ngắn hạn',
            'debt_to_equity': 'Tổng nợ phải trả / Vốn chủ sở hữu',
            'asset_turnover': 'Doanh thu / Tổng tài sản trung bình',
            'inventory_turnover': 'Giá vốn hàng bán / Hàng tồn kho trung bình',
            'eps': 'Lợi nhuận ròng / Số cổ phiếu phổ thông',
            'yoy_growth': '((Giá trị hiện tại - Giá trị năm trước) / Giá trị năm trước) × 100',
            'qoq_growth': '((Giá trị quý hiện tại - Giá trị quý trước) / Giá trị quý trước) × 100',
            'ttm_sum': 'Q1 + Q2 + Q3 + Q4',
            'ttm_avg': '(Q1 + Q2 + Q3 + Q4) / 4',
            'receivables_turnover': 'Doanh thu / Các khoản phải thu trung bình',
            'payables_turnover': 'Giá vốn hàng bán / Các khoản phải trả trung bình',
            'revenue_growth': '((Doanh thu hiện tại - Doanh thu kỳ trước) / Doanh thu kỳ trước) × 100',
            'profit_growth': '((Lợi nhuận hiện tại - Lợi nhuận kỳ trước) / Lợi nhuận kỳ trước) × 100',
            'free_cash_flow': 'Dòng tiền từ hoạt động kinh doanh - Chi tiêu vốn đầu tư'
        }
        
        return formulas.get(base_name, 'Công thức tính toán')
    
    def _generate_measurement(self, base_name: str) -> str:
        """Generate measurement description"""
        measurements = {
            'roe': 'Hiệu quả sử dụng vốn chủ sở hữu để tạo ra lợi nhuận',
            'roa': 'Hiệu quả sử dụng tổng tài sản để tạo ra lợi nhuận',
            'gross_margin': 'Tỷ lệ lợi nhuận gộp trên mỗi đồng doanh thu',
            'net_margin': 'Tỷ lệ lợi nhuận ròng trên mỗi đồng doanh thu',
            'operating_margin': 'Tỷ lệ lợi nhuận từ hoạt động kinh doanh cốt lõi',
            'current_ratio': 'Khả năng thanh toán các nghĩa vụ nợ ngắn hạn',
            'debt_to_equity': 'Mức độ sử dụng đòn bẩy tài chính',
            'asset_turnover': 'Hiệu quả sử dụng tài sản để tạo ra doanh thu',
            'inventory_turnover': 'Tốc độ bán hàng và quản lý tồn kho',
            'eps': 'Lợi nhuận phân bổ cho mỗi cổ phiếu phổ thông',
            'yoy_growth': 'Tốc độ tăng trưởng so với cùng kỳ năm trước',
            'qoq_growth': 'Tốc độ tăng trưởng so với quý trước',
            'ttm_sum': 'Tổng giá trị trong 12 tháng gần nhất',
            'ttm_avg': 'Trung bình giá trị trong 12 tháng gần nhất',
            'receivables_turnover': 'Tốc độ thu hồi các khoản phải thu',
            'payables_turnover': 'Tốc độ trả nợ cho nhà cung cấp',
            'revenue_growth': 'Tốc độ tăng trưởng doanh thu',
            'profit_growth': 'Tốc độ tăng trưởng lợi nhuận',
            'free_cash_flow': 'Dòng tiền thực tế tạo ra sau đầu tư'
        }
        
        return measurements.get(base_name, 'Financial metric measurement')
    
    def _generate_interpretation(self, base_name: str) -> str:
        """Generate interpretation with Vietnam benchmarks"""
        if base_name in self.vietnam_benchmarks:
            benchmarks = self.vietnam_benchmarks[base_name]
            lines = []
            for key, value in benchmarks.items():
                key_vi = {
                    'excellent': 'Xuất sắc',
                    'good': 'Tốt',
                    'acceptable': 'Chấp nhận được',
                    'poor': 'Kém',
                    'strong': 'Rất mạnh',
                    'moderate': 'Vừa phải',
                    'aggressive': 'Mạo hiểm',
                    'high_risk': 'Rủi ro cao',
                    'conservative': 'Bảo thủ',
                    'concern': 'Cần quan tâm',
                    'high': 'Cao',
                    'low': 'Thấp'
                }.get(key, key)
                
                lines.append(f'        - {value}: {key_vi}')
            
            return '\n'.join(lines)
        
        # Default interpretation for growth rates
        if 'growth' in base_name:
            return '''        - > 20%: Tăng trưởng vượt trội
        - 10-20%: Tăng trưởng rất tốt
        - 5-10%: Tăng trưởng tốt
        - 0-5%: Tăng trưởng vừa phải
        - < 0%: Sụt giảm'''
        
        # Default interpretation for TTM
        if 'ttm' in base_name:
            return '''        - Cung cấp cái nhìn toàn diện trong 12 tháng
        - Smooth out biến động theo mùa
        - Phù hợp cho so sánh và phân tích xu hướng'''
        
        return '        - Phụ thuộc vào ngành và điều kiện thị trường'
    
    def _generate_args(self, base_name: str) -> str:
        """Generate arguments description"""
        args_map = {
            'roe': 'net_income: Lợi nhuận sau thuế (VND)\n        equity: Vốn chủ sở hữu (VND)',
            'roa': 'net_income: Lợi nhuận sau thuế (VND)\n        total_assets: Tổng tài sản (VND)',
            'gross_margin': 'gross_profit: Lợi nhuận gộp (VND)\n        revenue: Doanh thu (VND)',
            'net_margin': 'net_profit: Lợi nhuận ròng (VND)\n        revenue: Doanh thu (VND)',
            'operating_margin': 'operating_profit: Lợi nhuận hoạt động (VND)\n        revenue: Doanh thu (VND)',
            'current_ratio': 'current_assets: Tài sản ngắn hạn (VND)\n        current_liabilities: Nợ ngắn hạn (VND)',
            'debt_to_equity': 'total_liabilities: Tổng nợ phải trả (VND)\n        equity: Vốn chủ sở hữu (VND)',
            'asset_turnover': 'revenue: Doanh thu (VND)\n        total_assets: Tổng tài sản trung bình (VND)',
            'inventory_turnover': 'cost_of_goods_sold: Giá vốn hàng bán (VND)\n        inventory: Hàng tồn kho trung bình (VND)',
            'eps': 'net_income: Lợi nhuận ròng (VND)\n        shares_outstanding: Số cổ phiếu phổ thông',
            'yoy_growth': 'current_value: Giá trị năm hiện tại\n        previous_value: Giá trị năm trước',
            'qoq_growth': 'current_value: Giá trị quý hiện tại\n        previous_value: Giá trị quý trước',
            'ttm_sum': 'q1: Giá trị quý 1\n        q2: Giá trị quý 2\n        q3: Giá trị quý 3\n        q4: Giá trị quý 4',
            'ttm_avg': 'q1: Giá trị quý 1\n        q2: Giá trị quý 2\n        q3: Giá trị quý 3\n        q4: Giá trị quý 4',
            'receivables_turnover': 'revenue: Doanh thu (VND)\n        accounts_receivable: Các khoản phải thu trung bình (VND)',
            'payables_turnover': 'cost_of_goods_sold: Giá vốn hàng bán (VND)\n        accounts_payable: Các khoản phải trả trung bình (VND)',
            'revenue_growth': 'current_revenue: Doanh thu kỳ hiện tại\n        previous_revenue: Doanh thu kỳ trước',
            'profit_growth': 'current_profit: Lợi nhuận kỳ hiện tại\n        previous_profit: Lợi nhuận kỳ trước',
            'free_cash_flow': 'operating_cash_flow: Dòng tiền từ hoạt động kinh doanh (VND)\n        capital_expenditure: Chi tiêu vốn đầu tư (VND)'
        }
        
        return args_map.get(base_name, 'Các tham số đầu vào')
    
    def _generate_returns(self, base_name: str) -> str:
        """Generate returns description"""
        if 'ratio' in base_name or 'margin' in base_name or 'growth' in base_name:
            return f'Tỷ lệ phần trăm (%), hoặc None nếu không hợp lệ'
        elif 'turnover' in base_name:
            return f'Tỷ lệ quay vòng (lần/năm), hoặc None nếu không hợp lệ'
        elif 'eps' in base_name:
            return f'Lợi nhuận trên mỗi cổ phiếu (VND), hoặc None nếu không hợp lệ'
        elif 'ttm' in base_name:
            return f'Giá trị TTM, hoặc None nếu không hợp lệ'
        elif 'flow' in base_name:
            return f'Dòng tiền (VND), hoặc None nếu không hợp lệ'
        else:
            return f'Giá trị tính toán, hoặc None nếu không hợp lệ'
    
    def _generate_examples(self, base_name: str) -> str:
        """Generate examples"""
        examples_map = {
            'roe': '        >>> calculate_roe(100_000_000_000, 500_000_000_000)\n        20.0  # 20% ROE',
            'roa': '        >>> calculate_roa(100_000_000_000, 2_000_000_000_000)\n        5.0   # 5% ROA',
            'gross_margin': '        >>> calculate_gross_margin(300_000_000_000, 1_000_000_000_000)\n        30.0  # 30% gross margin',
            'net_margin': '        >>> calculate_net_margin(100_000_000_000, 1_000_000_000_000)\n        10.0  # 10% net margin',
            'operating_margin': '        >>> calculate_operating_margin(150_000_000_000, 1_000_000_000_000)\n        15.0  # 15% operating margin',
            'current_ratio': '        >>> calculate_current_ratio(500_000_000_000, 200_000_000_000)\n        2.5   # 2.5 current ratio',
            'debt_to_equity': '        >>> calculate_debt_to_equity(800_000_000_000, 1_000_000_000_000)\n        0.8   # 0.8 debt-to-equity',
            'asset_turnover': '        >>> calculate_asset_turnover(2_000_000_000_000, 1_000_000_000_000)\n        2.0   # 2.0 asset turnover',
            'inventory_turnover': '        >>> calculate_inventory_turnover(600_000_000_000, 100_000_000_000)\n        6.0   # 6.0 inventory turnover',
            'eps': '        >>> calculate_eps(100_000_000_000, 10_000_000)\n        10_000  # 10,000 VND per share',
            'yoy_growth': '        >>> calculate_yoy_growth(120_000_000_000, 100_000_000_000)\n        20.0  # 20% YoY growth',
            'qoq_growth': '        >>> calculate_qoq_growth(115_000_000_000, 100_000_000_000)\n        15.0  # 15% QoQ growth',
            'ttm_sum': '        >>> calculate_ttm_sum(100_000_000_000, 120_000_000_000, 110_000_000_000, 130_000_000_000)\n        460_000_000_000  # TTM sum',
            'ttm_avg': '        >>> calculate_ttm_avg(100_000_000_000, 120_000_000_000, 110_000_000_000, 130_000_000_000)\n        115_000_000_000  # TTM average',
            'receivables_turnover': '        >>> calculate_receivables_turnover(1_000_000_000_000, 100_000_000_000)\n        10.0  # 10 times per year',
            'payables_turnover': '        >>> calculate_payables_turnover(600_000_000_000, 50_000_000_000)\n        12.0  # 12 times per year',
            'revenue_growth': '        >>> calculate_revenue_growth(120_000_000_000, 100_000_000_000)\n        20.0  # 20% revenue growth',
            'profit_growth': '        >>> calculate_profit_growth(24_000_000_000, 20_000_000_000)\n        20.0  # 20% profit growth',
            'free_cash_flow': '        >>> calculate_free_cash_flow(50_000_000_000, 30_000_000_000)\n        20_000_000_000  # 20 tỷ VND FCF'
        }
        
        return examples_map.get(base_name, '        # Example usage')
    
    def update_file_docstrings(self, file_path: Path) -> bool:
        """Update docstrings in a file"""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        functions = self.extract_function_info(file_path)
        if not functions:
            print(f"ℹ️  No functions found in {file_path}")
            return False
        
        modified = False
        lines = content.split('\n')
        
        # Process functions in reverse order to maintain line numbers
        for func_name, _, start_line, end_line in reversed(functions):
            # Find existing docstring
            docstring_start = None
            docstring_end = None
            
            for i in range(start_line, min(end_line, len(lines))):
                line = lines[i]
                if '"""' in line:
                    if docstring_start is None:
                        docstring_start = i
                    else:
                        docstring_end = i
                        break
            
            # Generate new docstring
            new_docstring = self.generate_vietnamese_docstring(func_name)
            
            # Replace docstring
            if docstring_start is not None and docstring_end is not None:
                # Replace existing docstring
                lines[docstring_start:docstring_end + 1] = [new_docstring]
                modified = True
                print(f"✅ Updated docstring for {func_name}")
            else:
                # Add docstring after function definition
                for i in range(start_line, min(end_line, len(lines))):
                    if 'def ' in lines[i] and ':' in lines[i]:
                        lines.insert(i + 1, new_docstring)
                        modified = True
                        print(f"✅ Added docstring for {func_name}")
                        break
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        
        return modified
    
    def run(self):
        """Run the docstring update process"""
        print("📝 Starting Vietnamese Docstring Update...")
        print("=" * 60)
        
        files_to_update = [
            self.formulas_dir / "_base_formulas.py",
            self.formulas_dir / "company_formulas.py",
            self.formulas_dir / "bank_formulas.py",
            self.valuation_formulas_dir / "valuation_formulas.py"
        ]
        
        files_modified = 0
        
        for file_path in files_to_update:
            print(f"\n📖 Processing: {file_path}")
            if self.update_file_docstrings(file_path):
                files_modified += 1
        
        print(f"\n" + "=" * 60)
        print(f"📋 SUMMARY: {files_modified} files modified")
        
        if files_modified > 0:
            print("\n🎯 Next Steps:")
            print("1. Test imports to ensure no syntax errors")
            print("2. Run formula tests to verify functionality")
            print("3. Commit changes: git commit -m 'feat: Add Vietnamese docstrings to all formulas'")
        else:
            print("\n✅ All docstrings already up to date")

if __name__ == "__main__":
    updater = VietnameseDocstringUpdater()
    updater.run()