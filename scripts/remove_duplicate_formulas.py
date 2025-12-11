#!/usr/bin/env python3
"""
Remove Duplicate Formulas Script - Xóa formulas trùng lặp
================================================================

Script này tự động xóa các duplicate formulas từ entity files,
chỉ giữ lại entity-specific formulas.

Usage:
    python scripts/remove_duplicate_formulas.py
"""

import os
import re
from pathlib import Path
from typing import List, Set

class DuplicateRemover:
    """Remove duplicate formulas from entity files"""
    
    def __init__(self):
        self.formulas_dir = Path("PROCESSORS/fundamental/formulas")
        
        # Universal formulas nên chỉ có trong _base_formulas.py
        self.universal_formulas = {
            'calculate_roe', 'calculate_roa', 'calculate_gross_margin', 
            'calculate_net_margin', 'calculate_operating_margin', 'calculate_current_ratio',
            'calculate_debt_to_equity', 'calculate_asset_turnover', 
            'calculate_inventory_turnover', 'calculate_eps', 'calculate_pe_ratio', 
            'calculate_pb_ratio'
        }
        
        # Entity-specific formulas cần giữ lại
        self.entity_specific_formulas = {
            'company': ['calculate_revenue_growth', 'calculate_profit_growth'],
            'bank': ['calculate_nim', 'calculate_cir', 'calculate_plr'],
            'insurance': ['calculate_combined_ratio', 'calculate_loss_ratio'],
            'security': ['calculate_cad_ratio', 'calculate_trading_leverage']
        }
    
    def remove_duplicates_from_file(self, file_path: Path, entity_type: str) -> bool:
        """
        Remove duplicate formulas from entity file
        
        Returns:
            bool: True if file was modified
        """
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        skip_lines = 0
        current_function = None
        functions_removed = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip if we're in a function to be removed
            if skip_lines > 0:
                skip_lines -= 1
                i += 1
                continue
            
            # Check for function definition
            func_match = re.match(r'^\s*def\s+(calculate_\w+)\s*\(', line)
            if func_match:
                func_name = func_match.group(1)
                current_function = func_name
                
                # Check if this is a duplicate formula
                if func_name in self.universal_formulas:
                    print(f"🗑️  Removing duplicate function: {func_name}")
                    functions_removed.append(func_name)
                    
                    # Skip until next function or end of class
                    skip_lines = 0
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if re.match(r'^\s*(def\s+|class\s+)', next_line):
                            break
                        skip_lines += 1
                        j += 1
                    
                    i += skip_lines + 1
                    continue
                else:
                    # Keep entity-specific functions
                    new_lines.append(line)
            else:
                new_lines.append(line)
            
            i += 1
        
        # Write back if modified
        if functions_removed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ Modified {file_path.name}")
            print(f"   Removed {len(functions_removed)} duplicate functions:")
            for func in functions_removed:
                print(f"   - {func}")
            
            return True
        else:
            print(f"✅ No duplicates found in {file_path.name}")
            return False
    
    def update_imports(self, file_path: Path) -> bool:
        """
        Update imports in calculator files to use _base_formulas
        """
        if 'calculator' not in file_path.name:
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already imports from _base_formulas
        if 'from PROCESSORS.fundamental.formulas._base_formulas import' in content:
            print(f"✅ {file_path.name} already imports from _base_formulas")
            return False
        
        # Find existing formula imports
        old_import_pattern = r'from PROCESSORS\.fundamental\.formulas\.\w+_formulas import.*'
        
        if re.search(old_import_pattern, content):
            # Replace with _base_formulas import
            new_import = 'from PROCESSORS.fundamental.formulas._base_formulas import ('
            
            # Add universal formulas to import
            universal_imports = ', '.join(sorted(self.universal_formulas))
            new_import += universal_imports + ')'
            
            content = re.sub(old_import_pattern, new_import, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated imports in {file_path.name}")
            return True
        
        return False
    
    def run(self):
        """Run duplicate removal process"""
        print("🗑️  Starting Duplicate Formula Removal...")
        print("=" * 60)
        
        # Process entity files
        entity_files = {
            'company': self.formulas_dir / "company_formulas.py",
            'bank': self.formulas_dir / "bank_formulas.py",
            'insurance': self.formulas_dir / "insurance_formulas.py",
            'security': self.formulas_dir / "security_formulas.py"
        }
        
        files_modified = 0
        
        for entity_type, file_path in entity_files.items():
            print(f"\n📖 Processing {entity_type}: {file_path}")
            
            if self.remove_duplicates_from_file(file_path, entity_type):
                files_modified += 1
        
        # Update calculator imports
        print(f"\n🔄 Updating calculator imports...")
        calculator_dir = Path("PROCESSORS/fundamental/calculators")
        
        for calculator_file in calculator_dir.glob("*_calculator.py"):
            if self.update_imports(calculator_file):
                files_modified += 1
        
        print(f"\n" + "=" * 60)
        print(f"📋 SUMMARY: {files_modified} files modified")
        
        if files_modified > 0:
            print("\n🎯 Next Steps:")
            print("1. Test calculators to ensure no import errors")
            print("2. Run formula audit again to verify duplicates removed")
            print("3. Add Vietnamese docstrings to remaining formulas")
        else:
            print("\n✅ No changes needed - duplicates already removed")

if __name__ == "__main__":
    remover = DuplicateRemover()
    remover.run()