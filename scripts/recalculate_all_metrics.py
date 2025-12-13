
import logging
from pathlib import Path
import os
import pandas as pd

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
from PROCESSORS.fundamental.calculators.insurance_calculator import InsuranceFinancialCalculator
from PROCESSORS.fundamental.calculators.security_calculator import SecurityFinancialCalculator
from WEBAPP.core.data_paths import DataPaths

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_calculator(entity_type, calculator_class, output_path):
    logger.info(f"Processing {entity_type}...")
    
    # input path (raw_fundamental used by calculator init)
    # Note: Calculators usually take the path to the raw parquet in __init__
    input_path = DataPaths.raw_fundamental(entity_type.lower())
    logger.info(f"Input: {input_path}")
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    try:
        calc = calculator_class(str(input_path))
        # Run full calculation pipeline
        # calculate_all_metrics usually returns nothing but populates internal state
        # or we might need to check specific methods
        
        # BaseFinancialCalculator has calculate() or similar?
        # Looking at code: it has calculate_all_metrics() which calls specific sub-methods.
        # It assumes we call load_data() first? 
        # BaseFinancialCalculator.__init__ calls nothing but setup.
        
        logger.info("Loading data...")
        calc.load_data()
        
        logger.info("Calculating metrics...")
        # pivot_data is called inside calculate_all_metrics usually? 
        # Let's check base class... 
        # process_data() is the main entry point in most implementations?
        # Actually, let's call the standard flow:
        # 1. load_data()
        # 2. pivot_data() -> creates self.pivot_df
        # 3. calculate_all_metrics() -> updates self.results/pivot_df
        
        # Let's verify CompanyCalculator methods.
        # It likely has a process() or similar.
        # BaseFinancialCalculator usually meant to be subclassed.
        
        # Checking logic from intuition:
        # calc.pivot_data() # Converts long to wide -> called inside calculate_all_metrics
        result_df = calc.calculate_all_metrics()
        
        if result_df.empty:
            logger.error(f"Calculation returned empty DataFrame for {entity_type}")
            return

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving to {output_path}...")
        result_df.to_parquet(output_path)
        logger.info(f"✅ {entity_type} complete.")

    except Exception as e:
        logger.error(f"❌ Error processing {entity_type}: {e}")
        import traceback
        traceback.print_exc()

def main():
    calculators = [
        ('COMPANY', CompanyFinancialCalculator, DataPaths.fundamental('company')),
        ('BANK', BankFinancialCalculator, DataPaths.fundamental('bank')),
        ('INSURANCE', InsuranceFinancialCalculator, DataPaths.fundamental('insurance')),
        ('SECURITY', SecurityFinancialCalculator, DataPaths.fundamental('security')),
    ]
    
    for name, cls, out_path in calculators:
        run_calculator(name, cls, out_path)

if __name__ == "__main__":
    main()
