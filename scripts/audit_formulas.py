#!/usr/bin/env python3
"""
Formula Audit Script - Kiểm tra trùng lặp và phân tích formulas
================================================================

Script này phân tích tất cả formulas trong các file để:
1. Tìm các functions trùng lặp giữa các files
2. Phân loại formulas (universal vs entity-specific)
3. Tạo báo cáo chi tiết về consolidation cần thiết

Usage:
    python scripts/audit_formulas.py
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class FormulaAuditor:
    """Auditor cho financial formulas"""
    
    def __init__(self):
        self.formulas_dir = Path("PROCESSORS/fundamental/formulas")
        self.formula_files = {
            'base': self.formulas_dir / "_base_formulas.py",
            'company': self.formulas_dir / "company_formulas.py", 
            'bank': self.formulas_dir / "bank_formulas.py",
            'insurance': self.formulas_dir / "insurance_formulas.py",
            'security': self.formulas_dir / "security_formulas.py"
        }
        
        # Universal formulas nên chỉ có trong _base_formulas.py
        self.universal_formulas = {
            'calculate_roe', 'calculate_roa', 'calculate_gross_margin', 
            'calculate_net_margin', 'calculate_operating_margin', 'safe_divide'
        }
        
        self.audit_results = {
            'all_formulas': defaultdict(list),
            'duplicates': defaultdict(list),
            'universal_in_entity_files': defaultdict(list),
            'entity_specific': defaultdict(list),
            'missing_docstrings': [],
            'formula_counts': {}
        }
    
    def extract_functions_from_file(self, file_path: Path) -> List[Tuple[str, str, str]]:
        """
        Extract function definitions from Python file
        
        Returns:
            List of (function_name, docstring, source_code)
        """
        if not file_path.exists():
            return []
            
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
                    # Extract docstring
                    docstring = ast.get_docstring(node) or ""
                    
                    # Extract source code (simplified)
                    source_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    source_code = '\n'.join(source_lines)
                    
                    functions.append((node.name, docstring, source_code))
        
        return functions
    
    def analyze_formula_similarity(self, func1: Tuple, func2: Tuple) -> float:
        """
        Calculate similarity between two functions based on name and docstring
        """
        name1, doc1, _ = func1
        name2, doc2, _ = func2
        
        # Name similarity (exact match for core formulas)
        if name1 == name2:
            return 1.0
        
        # Check for similar patterns (e.g., calculate_roe vs roe_calculation)
        base_name1 = name1.replace('calculate_', '')
        base_name2 = name2.replace('calculate_', '')
        
        if base_name1 == base_name2:
            return 0.9
        
        # Docstring similarity (simplified)
        if doc1 and doc2:
            # Extract formula line from docstring
            formula_pattern = r'Formula:\s*(.+)'
            formula1_match = re.search(formula_pattern, doc1)
            formula2_match = re.search(formula_pattern, doc2)
            
            if formula1_match and formula2_match:
                formula1 = formula1_match.group(1).strip()
                formula2 = formula2_match.group(1).strip()
                if formula1 == formula2:
                    return 0.8
        
        return 0.0
    
    def audit(self):
        """Run complete audit of all formulas"""
        print("🔍 Starting Formula Audit...")
        print("=" * 60)
        
        # Extract all functions
        all_functions = {}
        for file_type, file_path in self.formula_files.items():
            print(f"📖 Analyzing {file_type}: {file_path}")
            functions = self.extract_functions_from_file(file_path)
            all_functions[file_type] = functions
            
            # Store in audit results
            for func_name, docstring, source in functions:
                self.audit_results['all_formulas'][file_type].append(func_name)
        
        # Find duplicates
        print("\n🔄 Checking for duplicates...")
        self.find_duplicates(all_functions)
        
        # Check universal formulas in entity files
        print("\n⚠️  Checking universal formulas in entity files...")
        self.check_universal_formulas_in_entities(all_functions)
        
        # Categorize formulas
        print("\n📊 Categorizing formulas...")
        self.categorize_formulas(all_functions)
        
        # Check docstring quality
        print("\n📝 Checking docstring quality...")
        self.check_docstring_quality(all_functions)
        
        # Generate report
        self.generate_report()
    
    def find_duplicates(self, all_functions: Dict):
        """Find duplicate formulas across files"""
        function_map = defaultdict(list)
        
        for file_type, functions in all_functions.items():
            for func_name, _, _ in functions:
                function_map[func_name].append(file_type)
        
        # Find exact duplicates
        for func_name, file_types in function_map.items():
            if len(file_types) > 1:
                self.audit_results['duplicates'][func_name] = file_types
    
    def check_universal_formulas_in_entities(self, all_functions: Dict):
        """Check if universal formulas appear in entity-specific files"""
        entity_files = ['company', 'bank', 'insurance', 'security']
        
        for file_type in entity_files:
            if file_type not in all_functions:
                continue
                
            for func_name, _, _ in all_functions[file_type]:
                if func_name in self.universal_formulas:
                    self.audit_results['universal_in_entity_files'][file_type].append(func_name)
    
    def categorize_formulas(self, all_functions: Dict):
        """Categorize formulas as universal or entity-specific"""
        for file_type, functions in all_functions.items():
            for func_name, _, _ in functions:
                if func_name in self.universal_formulas:
                    self.audit_results['entity_specific']['universal'].append((file_type, func_name))
                else:
                    self.audit_results['entity_specific'][file_type].append(func_name)
        
        # Count formulas
        for file_type, functions in all_functions.items():
            self.audit_results['formula_counts'][file_type] = len(functions)
    
    def check_docstring_quality(self, all_functions: Dict):
        """Check for missing or poor docstrings"""
        for file_type, functions in all_functions.items():
            for func_name, docstring, _ in functions:
                if not docstring or len(docstring.strip()) < 20:
                    self.audit_results['missing_docstrings'].append((file_type, func_name))
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        report_path = Path("docs/formula_audit_report.md")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Formula Audit Report\n\n")
            f.write(f"**Generated:** {pd.Timestamp.now()}\n\n")
            
            # Summary
            f.write("## 📊 Summary\n\n")
            total_formulas = sum(self.audit_results['formula_counts'].values())
            f.write(f"- **Total Formulas:** {total_formulas}\n")
            f.write(f"- **Files Analyzed:** {len(self.formula_files)}\n")
            f.write(f"- **Duplicates Found:** {len(self.audit_results['duplicates'])}\n")
            f.write(f"- **Missing Docstrings:** {len(self.audit_results['missing_docstrings'])}\n\n")
            
            # Formula counts
            f.write("## 📈 Formula Counts by File\n\n")
            f.write("| File | Formula Count |\n")
            f.write("|------|---------------|\n")
            for file_type, count in self.audit_results['formula_counts'].items():
                f.write(f"| {file_type} | {count} |\n")
            f.write("\n")
            
            # Duplicates
            if self.audit_results['duplicates']:
                f.write("## 🔄 Duplicate Formulas\n\n")
                f.write("The following formulas appear in multiple files:\n\n")
                for func_name, file_types in self.audit_results['duplicates'].items():
                    f.write(f"### `{func_name}`\n")
                    f.write(f"**Found in:** {', '.join(file_types)}\n")
                    f.write("**Action:** Keep only in `_base_formulas.py`\n\n")
            
            # Universal formulas in entity files
            if self.audit_results['universal_in_entity_files']:
                f.write("## ⚠️ Universal Formulas in Entity Files\n\n")
                for file_type, formulas in self.audit_results['universal_in_entity_files'].items():
                    if formulas:
                        f.write(f"### {file_type.title()}.py\n")
                        for formula in formulas:
                            f.write(f"- `{formula}` - Should be removed\n")
                        f.write("\n")
            
            # Missing docstrings
            if self.audit_results['missing_docstrings']:
                f.write("## 📝 Missing or Poor Docstrings\n\n")
                for file_type, func_name in self.audit_results['missing_docstrings']:
                    f.write(f"- `{file_type}.py`: `{func_name}`\n")
                f.write("\n")
            
            # Recommendations
            f.write("## 🎯 Recommendations\n\n")
            f.write("### 1. Immediate Actions (Phase 1)\n\n")
            f.write("1. **Remove Duplicates:**\n")
            f.write("   - Move universal formulas to `_base_formulas.py`\n")
            f.write("   - Remove from entity-specific files\n")
            f.write("   - Update imports in calculators\n\n")
            
            f.write("2. **Fix Docstrings:**\n")
            f.write("   - Add comprehensive Vietnamese docstrings\n")
            f.write("   - Include formula, interpretation, examples\n\n")
            
            f.write("### 2. Consolidation Strategy\n\n")
            f.write("1. **Keep in _base_formulas.py:**\n")
            for formula in sorted(self.universal_formulas):
                f.write(f"   - `{formula}`\n")
            f.write("\n")
            
            f.write("2. **Entity-Specific to Keep:**\n")
            entity_specific = {
                'company': ['asset_turnover', 'inventory_turnover'],
                'bank': ['nim', 'cir', 'plr'],
                'insurance': ['combined_ratio', 'loss_ratio'],
                'security': ['cad_ratio', 'trading_leverage']
            }
            
            for entity, formulas in entity_specific.items():
                f.write(f"   **{entity.title()}:**\n")
                for formula in formulas:
                    f.write(f"   - `{formula}`\n")
                f.write("\n")
        
        print(f"✅ Audit report generated: {report_path}")
        
        # Print summary to console
        self.print_summary()
    
    def print_summary(self):
        """Print audit summary to console"""
        print("\n" + "=" * 60)
        print("📋 AUDIT SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Formula Counts:")
        for file_type, count in self.audit_results['formula_counts'].items():
            print(f"  {file_type:12} : {count:3} formulas")
        
        if self.audit_results['duplicates']:
            print(f"\n🔄 Duplicates Found: {len(self.audit_results['duplicates'])}")
            for func_name, file_types in self.audit_results['duplicates'].items():
                print(f"  ❌ {func_name}: {', '.join(file_types)}")
        
        if self.audit_results['universal_in_entity_files']:
            print(f"\n⚠️  Universal Formulas in Entity Files:")
            for file_type, formulas in self.audit_results['universal_in_entity_files'].items():
                if formulas:
                    print(f"  {file_type.title()}: {len(formulas)} formulas")
        
        print(f"\n📝 Missing Docstrings: {len(self.audit_results['missing_docstrings'])}")
        
        print("\n🎯 Key Actions Needed:")
        print("  1. Remove duplicate formulas from entity files")
        print("  2. Consolidate universal formulas in _base_formulas.py")
        print("  3. Add Vietnamese docstrings to all formulas")
        print("  4. Update calculator imports")

if __name__ == "__main__":
    import pandas as pd
    
    auditor = FormulaAuditor()
    auditor.audit()