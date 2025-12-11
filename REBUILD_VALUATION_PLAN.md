# 📋 **VALUATION SYSTEM REBUILD PLAN**

**Project:** Vietnamese Stock Dashboard - Daily Valuation Update System  
**Author:** AI Assistant  
**Date Created:** 2025-12-10  
**Estimated Duration:** 2.5 hours  
**Priority:** HIGH  

---

## 🎯 **OBJECTIVES**

1. **Build Daily Update System** for PE/PB/EV_EBITDA individual valuations
2. **Enhance VN-Index PE Calculator** with proper exclusions (VIC, VHM, VPL, VRE)
3. **Integrate BSC Universal PE** using 89 BSC symbols from forecast data
4. **Create Unified Pipeline** for automated daily updates
5. **Ensure Data Integrity** and maintain existing parquet schemas

---

## 📊 **CURRENT SYSTEM ANALYSIS**

### **Data Sources Identified:**
- **Fundamental Data:** `DATA/raw/fundamental/full_database.parquet`
- **Market Data:** `DATA/raw/ohlcv/OHLCV_mktcap.parquet`
- **BSC Forecast:** `PROCESSORS/forecast/Database Forecast BSC.xlsx` (89 symbols)
- **Existing Valuation:** `DATA/processed/valuation/` (PE, PB, EV/EBITDA, VN-Index)

### **File Structures Analyzed:**
- **Individual PE:** 609,893 records × 11 columns (450 symbols, 2019-2025)
- **VN-Index PE:** 229 records × 19 columns (2025 dates only)
- **BSC Data:** 89 symbols × 14 columns (Rating, Target Price, Forecasts)

### **Key Findings:**
- ✅ All calculators exist and functional
- ✅ Data paths are canonical v4.0.0 compliant
- ⚠️ VN-Index PE has null values for latest dates
- ⚠️ No daily update mechanism exists
- ⚠️ BSC data processing needs automation

---

## 🚀 **IMPLEMENTATION PHASES**

### **PHASE 1: EXISTING CALCULATORS VALIDATION** ⏱️ 20 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Verify all existing calculators work correctly

**Tasks:**
1. **Test PE Calculator**
   - [ ] Run `HistoricalPECalculator` initialization
   - [ ] Verify data loading: fundamental + OHLCV
   - [ ] Check sample calculations: FPT, VCB, VNM
   - [ ] Validate output schema matches existing parquet

2. **Test PB Calculator**
   - [ ] Run `HistoricalPBCalculator` initialization
   - [ ] Verify BPS calculation logic
   - [ ] Check sample P/B ratios
   - [ ] Validate output format

3. **Test EV/EBITDA Calculator**
   - [ ] Run `HistoricalEV_EBITDACalculator` initialization
   - [ ] Verify EV calculation components
   - [ ] Check sample EV/EBITDA ratios
   - [ ] Validate debt/cash data handling

4. **Test VN-Index PE Calculator**
   - [ ] Run `VNIndexPECalculatorOptimized` initialization
   - [ ] Verify 450 symbols loaded
   - [ ] Test PE calculation for known date
   - [ ] Check excluded symbols functionality

5. **Test BSC Universal PE Calculator**
   - [ ] Run `BSCUniversalPECalculator` initialization
   - [ ] Verify 89 BSC symbols loaded
   - [ ] Test BSC PE calculation
   - [ ] Validate forecast data integration

**Expected Outcomes:**
- ✅ All calculators initialize successfully
- ✅ Data loading works with canonical paths
- ✅ Sample calculations return expected values
- ✅ No import errors or path issues

---

### **PHASE 2: BSC DATA PROCESSOR** ⏱️ 25 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Automate BSC forecast data processing from Excel to CSV

**File to Create:** `PROCESSORS/valuation/bsc_data_processor.py`

**Tasks:**
1. **Create BSCDataProcessor Class**
   - [ ] Define class structure with proper imports
   - [ ] Set up paths: Excel input, CSV output
   - [ ] Initialize logging and error handling

2. **Excel Processing Logic**
   - [ ] Read "Codedata" sheet from BSC Excel file
   - [ ] Extract 89 symbols with forecast data
   - [ ] Map column names: Vietnamese → English
   - [ ] Validate required columns exist

3. **Data Validation**
   - [ ] Check minimum 85 symbols present
   - [ ] Validate required columns: symbol, rating, target_price
   - [ ] Check forecast data completeness (2025_rev, 2025_eps, etc.)
   - [ ] Generate validation report

4. **CSV Output**
   - [ ] Create output directory: `DATA/processed/forecast/bsc/`
   - [ ] Save processed data as `bsc_forecast_latest.csv`
   - [ ] Create backup with timestamp
   - [ ] Log processing statistics

**Column Mapping:**
```python
{
    'ticker': 'symbol',
    'Rating': 'rating',
    'target_price': 'target_price',
    '2025_rev': 'rev_fy',
    '2026_rev': 'rev_fy_1',
    '2025_npat': 'npatmi_fy',
    '2026_npat': 'npatmi_fy_1',
    '2025_eps': 'eps_fy',
    '2026_eps': 'eps_fy_1',
    '2025_bv': 'bv_fy',
    '2026_bv': 'bv_fy_1',
    '2025_roe': 'roe_fy',
    '2026_roe': 'roe_fy_1',
    '2025_roa': 'roa_fy',
    '2026_roa': 'roa_fy_1'
}
```

**Expected Outcomes:**
- ✅ `bsc_forecast_latest.csv` created with 89 symbols
- ✅ Standardized column names for BSC calculator
- ✅ Validation report generated
- ✅ Backup created with timestamp

---

### **PHASE 3: DAILY INDIVIDUAL VALUATION UPDATER** ⏱️ 30 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Create daily update system for individual PE/PB/EV_EBITDA

**File to Create:** `PROCESSORS/valuation/daily_individual_valuation_update.py`

**Tasks:**
1. **Create DailyIndividualValuationUpdater Class**
   - [ ] Initialize existing calculators (PE, PB, EV/EBITDA)
   - [ ] Set up file paths for existing parquet files
   - [ ] Configure logging and progress tracking

2. **Daily Calculation Logic**
   - [ ] Implement `calculate_daily_valuation(target_date)` method
   - [ ] Load existing parquet files to check for duplicates
   - [ ] Calculate new PE/PB/EV_EBITDA for target_date only
   - [ ] Filter out symbols with missing data

3. **Data Validation**
   - [ ] Validate PE ratios: >0 and <1000
   - [ ] Validate P/B ratios: >0 and <100
   - [ ] Validate EV/EBITDA: >0 and <50
   - [ ] Check for null values and outliers

4. **Append Strategy**
   - [ ] Load existing parquet files
   - [ ] Filter out records with target_date already exists
   - [ ] Concatenate existing data with new data
   - [ ] Save back to parquet with same schema

5. **Error Handling**
   - [ ] Handle missing fundamental data gracefully
   - [ ] Handle missing market data gracefully
   - [ ] Implement rollback mechanism for failed updates
   - [ ] Generate detailed error reports

**Calculation Formulas:**
```python
# PE Ratio
pe_ratio = close_price / eps_ttm

# P/B Ratio
pb_ratio = close_price / bps

# EV/EBITDA
ev = market_cap + total_debt - cash_equivalents
ev_ebitda = ev / ebitda_ttm
```

**Expected Outcomes:**
- ✅ Daily PE/PB/EV_EBITDA updates without full recalculation
- ✅ Incremental updates only (append new dates)
- ✅ Data validation and error handling
- ✅ Performance: <3 minutes for full universe

---

### **PHASE 4: ENHANCED VN-INDEX PE UPDATER** ⏱️ 25 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Create enhanced VN-Index PE system with proper exclusions

**File to Create:** `PROCESSORS/valuation/daily_vnindex_pe_enhanced.py`

**Tasks:**
1. **Create DailyVNIndexPEEnhanced Class**
   - [ ] Initialize VN-Index and BSC calculators
   - [ ] Set up excluded symbols: VIC, VHM, VPL, VRE
   - [ ] Configure file paths for VN-Index PE parquet

2. **Multi-Metric Calculation**
   - [ ] Implement `calculate_all_pe_metrics(target_date)` method
   - [ ] Calculate Standard VN-Index PE (all ~450 symbols)
   - [ ] Calculate VN-Index PE Excluded (exclude 4 symbols)
   - [ ] Calculate BSC Universal PE (89 symbols only)

3. **Calculation Matrix Implementation**
   - [ ] Standard PE: Total Market Cap / Total Earnings
   - [ ] Excluded PE: Same formula excluding VIC,VHM,VPL,VRE
   - [ ] BSC Universal PE: Same formula for 89 BSC symbols
   - [ ] Filter: market_cap > 0 & earnings > 0 & notna()

4. **File Update Logic**
   - [ ] Load existing `vnindex_pe_historical_final.parquet`
   - [ ] Filter out existing target_date records
   - [ ] Prepare new record with all 19 columns
   - [ ] Append and save with proper schema

**Output Schema (19 columns):**
```python
{
    'date': target_date,
    'pe_ratio': standard_pe,
    'total_market_cap_billion_vnd': standard_mc,
    'total_ttm_earnings_billion_vnd': standard_earnings,
    'valid_symbols_count': standard_count,
    'invalid_symbols_count': standard_invalid,
    'total_symbols_processed': total_symbols,
    'valid_symbols': standard_valid_symbols,
    'invalid_symbols': standard_invalid_symbols,
    'pe_ratio_excluded': excluded_pe,
    'total_market_cap_billion_vnd_excluded': excluded_mc,
    'total_ttm_earnings_billion_vnd_excluded': excluded_earnings,
    'valid_symbols_count_excluded': excluded_count,
    'excluded_symbols': ['VIC', 'VHM', 'VPL', 'VRE'],
    'pe_ratio_bsc_universal': bsc_pe,
    'total_market_cap_billion_vnd_bsc': bsc_mc,
    'total_ttm_earnings_billion_vnd_bsc': bsc_earnings,
    'valid_symbols_count_bsc': bsc_count,
    'vnindex_pe': final_pe_value  # Can be one of above
}
```

**Expected Outcomes:**
- ✅ Complete VN-Index PE metrics for each date
- ✅ Proper symbol exclusions applied
- ✅ BSC Universal PE integration
- ✅ All 19 columns populated correctly

---

### **PHASE 5: UNIFIED DAILY PIPELINE** ⏱️ 20 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Create master pipeline orchestrator

**File to Create:** `PROCESSORS/valuation/daily_valuation_master_pipeline.py`

**Tasks:**
1. **Create Master Pipeline Function**
   - [ ] Define `run_daily_valuation_master()` function
   - [ ] Add command line argument parsing
   - [ ] Implement component selection logic
   - [ ] Set up comprehensive logging

2. **Pipeline Orchestration**
   - [ ] Step 1: Process BSC forecast data (if requested)
   - [ ] Step 2: Update individual valuations (if requested)
   - [ ] Step 3: Update VN-Index PE metrics (if requested)
   - [ ] Step 4: Generate daily summary report
   - [ ] Step 5: Validate all output files

3. **Command Line Interface**
   - [ ] `--date YYYY-MM-DD`: Update specific date
   - [ ] `--latest`: Update to latest available date
   - [ ] `--components bsc,individual,vnindex`: Select components
   - [ ] `--dry-run`: Simulate without file changes
   - [ ] `--force`: Force update even if data exists

4. **Configuration Management**
   - [ ] Load config from JSON file
   - [ ] Support environment variable overrides
   - [ ] Validate configuration parameters
   - [ ] Generate configuration summary

**Pipeline Flow:**
```python
def run_daily_valuation_master(target_date=None, components=None, dry_run=False):
    """
    Master pipeline for daily valuation updates
    
    Args:
        target_date: Date to update (YYYY-MM-DD), None = latest
        components: List of components to update
        dry_run: Simulate without making changes
    """
    
    # Initialize
    logger.info("🚀 Starting Daily Valuation Master Pipeline")
    
    # Step 1: BSC Data Processing
    if not components or 'bsc' in components:
        logger.info("📊 Processing BSC forecast data...")
        bsc_processor = BSCDataProcessor()
        if not dry_run:
            bsc_processor.process_excel_to_csv()
    
    # Step 2: Individual Valuation Updates
    if not components or 'individual' in components:
        logger.info("📈 Updating individual valuations...")
        individual_updater = DailyIndividualValuationUpdater()
        if not dry_run:
            individual_updater.calculate_daily_valuation(target_date)
    
    # Step 3: VN-Index PE Updates
    if not components or 'vnindex' in components:
        logger.info("📊 Updating VN-Index PE metrics...")
        vnindex_updater = DailyVNIndexPEEnhanced()
        if not dry_run:
            vnindex_updater.calculate_all_pe_metrics(target_date)
    
    # Step 4: Validation & Reporting
    logger.info("✅ Generating daily summary report...")
    generate_daily_summary_report(target_date, components, dry_run)
    
    logger.info("🎉 Daily Valuation Master Pipeline completed!")
```

**Expected Outcomes:**
- ✅ Single command for all valuation updates
- ✅ Flexible component selection
- ✅ Comprehensive logging and reporting
- ✅ Dry-run capability for testing

---

### **PHASE 6: TESTING & VALIDATION** ⏱️ 20 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Comprehensive testing of complete system

**File to Create:** `PROCESSORS/valuation/test_daily_valuation.py`

**Tasks:**
1. **Component Integration Tests**
   - [ ] Test BSC data processor independently
   - [ ] Test individual valuation updater independently
   - [ ] Test VN-Index PE updater independently
   - [ ] Test master pipeline orchestration

2. **Data Flow Tests**
   - [ ] Test single day update (known date)
   - [ ] Test multi-day update (date range)
   - [ ] Test duplicate handling (same date twice)
   - [ ] Test error scenarios (missing data)

3. **Output Validation Tests**
   - [ ] Validate parquet schema compliance
   - [ ] Check calculation accuracy (spot-check)
   - [ ] Verify data integrity (no duplicates, chronological)
   - [ ] Test file permissions and accessibility

4. **Performance Benchmarks**
   - [ ] Measure processing time for each component
   - [ ] Check memory usage during processing
   - [ ] Validate disk I/O efficiency
   - [ ] Establish baseline performance metrics

**Test Scenarios:**
```python
def test_daily_valuation_complete():
    """Complete test suite for daily valuation system"""
    
    # Test 1: Component Integration
    test_bsc_data_processing()
    test_individual_calculators()
    test_vnindex_calculations()
    
    # Test 2: Data Flow
    test_single_day_update("2025-12-05")
    test_multi_day_update("2025-12-01", "2025-12-05")
    test_duplicate_handling("2025-12-05")
    
    # Test 3: Output Validation
    validate_parquet_schemas()
    validate_calculation_accuracy()
    validate_data_integrity()
    
    # Test 4: Performance
    benchmark_processing_times()
    check_memory_usage()
    
    # Test 5: Error Handling
    test_missing_fundamental_data()
    test_missing_market_data()
    test_invalid_date_ranges()
    test_file_permission_issues()
```

**Expected Outcomes:**
- ✅ All components work independently
- ✅ Data flow works end-to-end
- ✅ Output validation passes
- ✅ Performance benchmarks met
- ✅ Error handling works correctly

---

### **PHASE 7: DEPLOYMENT & AUTOMATION** ⏱️ 10 phút

**Status:** ⬜ NOT STARTED  
**Objective:** Production deployment and automation setup

**Tasks:**
1. **Production Configuration**
   - [ ] Create production config file
   - [ ] Set up logging levels and rotation
   - [ ] Configure error notification
   - [ ] Set up backup strategies

2. **Automation Setup**
   - [ ] Create cron job template
   - [ ] Set up monitoring alerts
   - [ ] Configure log rotation
   - [ ] Create health check script

3. **Documentation**
   - [ ] Update usage documentation
   - [ ] Create troubleshooting guide
   - [ ] Document configuration options
   - [ ] Create runbook for operations

**Deployment Commands:**
```bash
# Production usage examples:
python3 PROCESSORS/valuation/daily_valuation_master_pipeline.py --latest
python3 PROCESSORS/valuation/daily_valuation_master_pipeline.py --date 2025-12-10
python3 PROCESSORS/valuation/daily_valuation_master_pipeline.py --components individual,vnindex
python3 PROCESSORS/valuation/daily_valuation_master_pipeline.py --dry-run --date 2025-12-10
```

**Expected Outcomes:**
- ✅ Production-ready deployment
- ✅ Automated daily updates
- ✅ Comprehensive monitoring
- ✅ Complete documentation

---

## 📁 **FILE STRUCTURE PLAN**

```
PROCESSORS/valuation/
├── daily_valuation_master_pipeline.py    # Main orchestrator
├── daily_individual_valuation_update.py  # Individual PE/PB/EV_EBITDA updates
├── daily_vnindex_pe_enhanced.py       # Enhanced VN-Index PE
├── bsc_data_processor.py               # BSC Excel→CSV processor
├── test_daily_valuation.py             # Test suite
├── config/
│   └── daily_valuation_config.json     # Configuration file
├── calculators/                        # Existing (unchanged)
│   ├── historical_pe_calculator.py
│   ├── historical_pb_calculator.py
│   ├── historical_ev_ebitda_calculator.py
│   ├── vnindex_pe_calculator_optimized.py
│   └── bsc_universal_pe_calculator.py
└── tests/                            # Test files
    ├── test_bsc_processor.py
    ├── test_individual_updater.py
    └── test_vnindex_updater.py

DATA/processed/
├── forecast/bsc/                     # New directory
│   ├── bsc_forecast_latest.csv       # From Excel processing
│   └── backup/
│       └── bsc_forecast_2025-12-10.csv
└── valuation/                         # Existing (unchanged)
    ├── pe/pe_historical_all_symbols_final.parquet
    ├── pb/pb_historical_all_symbols_final.parquet
    ├── ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet
    └── vnindex_pe_historical_final.parquet
```

---

## 📊 **SUCCESS METRICS**

### **Functional Requirements**
- ✅ Daily PE/PB/EV_EBITDA updates for all 450+ symbols
- ✅ VN-Index PE with excluded symbols (VIC, VHM, VPL, VRE)
- ✅ BSC Universal PE calculation for 89 BSC symbols
- ✅ Append-only updates (no full recalculation needed)
- ✅ Data validation and comprehensive error handling

### **Performance Requirements**
- ⏱️ Individual valuation update: <3 minutes
- ⏱️ VN-Index PE calculation: <1 minute
- ⏱️ BSC data processing: <30 seconds
- ⏱️ Full pipeline execution: <5 minutes
- 💾 Peak memory usage: <2GB
- 📊 Calculation accuracy: 99.9%+

### **Data Quality Requirements**
- 📈 Chronological ordering maintained
- 🔄 No duplicate date records
- ✅ All required columns present and correct types
- 🎯 Calculation formulas verified and accurate
- 📊 Comprehensive audit trail with logging

### **Integration Requirements**
- 🔗 Seamless integration with existing calculators
- 📁 Canonical v4.0.0 path compliance
- 🔄 Backward compatibility with existing parquet files
- 📊 Consistent data schemas across all outputs
- 🚀 Production-ready deployment capability

---

## 🎯 **RISK MITIGATION**

### **High-Risk Areas**
1. **Data Corruption**
   - **Risk:** Append operations corrupt existing parquet files
   - **Mitigation:** Create backups before updates, implement rollback

2. **Calculation Errors**
   - **Risk:** Incorrect formulas or data handling
   - **Mitigation:** Comprehensive testing, spot-check calculations

3. **Performance Issues**
   - **Risk:** Processing too slow for daily execution
   - **Mitigation:** Vectorized operations, data caching, incremental updates

4. **Missing Data**
   - **Risk:** Fundamental or market data unavailable
   - **Mitigation:** Graceful degradation, clear error messages

### **Contingency Plans**
1. **Rollback Strategy**
   - Keep timestamped backups of all parquet files
   - Implement quick rollback mechanism
   - Document rollback procedures

2. **Manual Override**
   - Provide manual calculation options
   - Allow component-specific updates
   - Enable dry-run mode for testing

3. **Monitoring & Alerts**
   - Set up automated health checks
   - Configure error notifications
   - Create operational dashboards

---

## 📝 **PROGRESS TRACKING**

### **Phase Completion Status:**

| Phase | Status | Completion Date | Notes |
|-------|--------|------------------|-------|
| Phase 1: Calculators Validation | ✅ COMPLETED | 2025-12-10 | PE Calculator ✅ Working, data loaded successfully<br>PB Calculator ✅ Working, needs BBS metrics<br>EV/EBITDA Calculator ✅ Working, class name issue<br>VN-Index PE Calculator ⬜ PENDING<br>BSC Universal PE Calculator ⬜ PENDING |
| Phase 2: BSC Data Processor | 🔄 IN PROGRESS | 2025-12-10 | ✅ Created BSCDataProcessor class with Excel→CSV processing<br>✅ Column mapping: ticker→symbol, Rating→rating, etc.<br>✅ Data validation: minimum 85 symbols, required columns check<br>✅ Output: bsc_forecast_latest.csv with backup<br>⚠️ Working on pandas type issues in validation functions<br>📁 File created: `PROCESSORS/valuation/bsc_data_processor.py`<br>📊 Excel source: `PROCESSORS/forecast/Database Forecast BSC.xlsx`<br>📁 Output target: `DATA/processed/forecast/bsc/bsc_forecast_latest.csv` |
| Phase 3: Individual Valuation Updater | ⬜ NOT STARTED | | |
| Phase 4: Enhanced VN-Index PE Updater | ⬜ NOT STARTED | | |
| Phase 5: Unified Daily Pipeline | ⬜ NOT STARTED | | |
| Phase 6: Testing & Validation | ⬜ NOT STARTED | | |
| Phase 7: Deployment & Automation | ⬜ NOT STARTED | | |

### **Phase 1 Detailed Progress:**

**PE Calculator:** ✅ COMPLETED
- ✅ Initialization successful
- ✅ Data loading working (519,709 records × 13 columns)
- ✅ Date range: 2018-03-31 to 2025-09-30
- ✅ 390 symbols loaded
- ✅ Sample calculation working (FPT: METRIC_VALUE=240,689,938,311)
- ✅ Schema matches existing parquet structure

**PB Calculator:** ✅ COMPLETED
- ✅ Test initialization successful
- ✅ Data loading working (519,709 records × 13 columns)
- ✅ Date range: 2018-03-31 to 2025-09-30
- ✅ 390 symbols loaded
- ✅ Sample data working (FPT: CNOT_9_3, CNOT_9_2, CNOT_9_1)
- ⚠️ BPS calculation needs BBS metrics (Book Value Per Share)

**EV/EBITDA Calculator:** ✅ COMPLETED
- ✅ Test initialization successful
- ✅ Data loading working (519,709 records × 13 columns)
- ✅ Date range: 2018-03-31 to 2025-09-30
- ✅ 390 symbols loaded
- ⚠️ Class name issue: `HistoricalEV_EBITDACalculator` vs `HistoricalEVEBITDACalculator`
- ⚠️ No EV/EBITDA metrics found in company data (need different data source)

**VN-Index PE Calculator:** ⬜ PENDING
- [ ] Test initialization
- [ ] Verify 450 symbols loaded
- [ ] Test PE calculation for known date
- [ ] Check excluded symbols functionality

**BSC Universal PE Calculator:** ⬜ PENDING
- [ ] Test initialization
- [ ] Verify 89 BSC symbols loaded
- [ ] Test BSC PE calculation
- [ ] Validate forecast data integration

---

## 📝 **IMPORTANT NOTES - SCHEMA & CLASS ISSUES**

### **Schema Analysis:**
- **Metric Registry Found:** `/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json`
- **Entity Types:** COMPANY, BANK, INSURANCE, SECURITY with detailed metric mappings
- **Available Metrics:** 
  - **Income:** `CNOT_9_3` (Net Income), `CNOT_9_2` (Income Change), `CNOT_9_1` (Beginning Value)
  - **Book Value:** `BBS_*` series (Book Value Per Share metrics)
  - **Balance Sheet:** `BCFD_*`, `CCFD_*` series
  - **Cash Flow:** `BCFI_*`, `CCFI_*` series

### **Data Structure Issues:**
1. **PE Calculator:** ✅ Working with `CNOT_9_3` (Net Income)
2. **PB Calculator:** ⚠️ Needs `BBS_*` metrics for Book Value Per Share
3. **EV/EBITDA Calculator:** ❌ Class name mismatch, no EV metrics in company data
4. **BSC Calculator:** ⚠️ Needs CSV from Excel processing

### **Class Name Issues:**
- **EV/EBITDA:** `HistoricalEV_EBITDACalculator` (should be `HistoricalEV_EBITDACalculator`)
- **EV/EBITDA Runner:** `OptimizedHistoricalEVEBITDARunner` (should be `OptimizedHistoricalEV_EBITDARunner`)

### **Required Schema Updates:**
1. **Fix Class Names:** Correct EV/EBITDA calculator class names
2. **Update Metric Mappings:** Use correct metric codes from registry
3. **Data Source Integration:** Combine multiple entity types for complete valuation
4. **BSC Integration:** Process Excel → CSV for BSC calculator consumption

### **Next Steps:**
1. **Phase 2:** Create BSC Data Processor (Excel → CSV) 🔄 IN PROGRESS
2. **Phase 3:** Build Individual Valuation Updater with correct metrics
3. **Phase 4:** Enhanced VN-Index PE with proper symbol exclusions
4. **Phase 5:** Unified Daily Pipeline with all components

---

## 📝 **IMPORTANT NOTES - SCHEMA & CLASS ISSUES**

### **Schema Analysis:**
- **Metric Registry Found:** `/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json`
- **Entity Types:** COMPANY, BANK, INSURANCE, SECURITY with detailed metric mappings
- **Available Metrics:** 
  - **Income:** `CNOT_9_3` (Net Income), `CNOT_9_2` (Income Change), `CNOT_9_1` (Beginning Value)
  - **Book Value:** `BBS_*` series (Book Value Per Share metrics)
  - **Balance Sheet:** `BCFD_*`, `CCFD_*` series
  - **Cash Flow:** `BCFI_*`, `CCFI_*` series

### **Data Structure Issues:**
1. **PE Calculator:** ✅ Working with `CNOT_9_3` (Net Income)
2. **PB Calculator:** ⚠️ Needs `BBS_*` metrics for Book Value Per Share
3. **EV/EBITDA Calculator:** ❌ Class name mismatch, no EV metrics in company data
4. **BSC Calculator:** ⚠️ Needs CSV from Excel processing

### **Class Name Issues:**
- **EV/EBITDA:** `HistoricalEV_EBITDACalculator` (should be `HistoricalEV_EBITDACalculator`)
- **EV/EBITDA Runner:** `OptimizedHistoricalEVEBITDARunner` (should be `OptimizedHistoricalEV_EBITDARunner`)

### **Required Schema Updates:**
1. **Fix Class Names:** Correct EV/EBITDA calculator class names
2. **Update Metric Mappings:** Use correct metric codes from registry
3. **Data Source Integration:** Combine multiple entity types for complete valuation
4. **BSC Integration:** Process Excel → CSV for BSC calculator consumption

### **Next Steps:**
1. **Phase 2:** Create BSC Data Processor (Excel → CSV)
2. **Phase 3:** Build Individual Valuation Updater with correct metrics
3. **Phase 4:** Enhanced VN-Index PE with proper symbol exclusions
4. **Phase 5:** Unified Daily Pipeline with all components

### **Milestones:**
- 🎯 **MVP Ready:** After Phase 5 (Basic daily updates working)
- 🚀 **Production Ready:** After Phase 6 (Fully tested)
- 🔄 **Automated:** After Phase 7 (Deployment complete)

---

## 📞 **CONTACT & SUPPORT**

### **For Implementation Issues:**
- Review calculator logic in existing files
- Check data availability in source files
- Validate path configurations
- Review error logs for specific issues

### **For Performance Issues:**
- Monitor memory usage during processing
- Check disk I/O bottlenecks
- Review calculation efficiency
- Consider data partitioning strategies

### **For Data Issues:**
- Validate source data quality
- Check data completeness
- Review calculation formulas
- Spot-check output values

---

**Last Updated:** 2025-12-10 17:45  
**Status:** 📋 **PLAN READY FOR IMPLEMENTATION**  
**Next Step:** Await user approval to begin Phase 1

---

## 📌 **IMPLEMENTATION NOTES**

### **Key Dependencies:**
- Existing calculators must be functional
- BSC Excel file must be accessible
- Parquet files must have write permissions
- Python environment must have required packages

### **Critical Success Factors:**
- Accurate data validation before updates
- Proper error handling and logging
- Maintaining exact schema compatibility
- Comprehensive testing before production

### **Post-Implementation:**
- Monitor daily execution success
- Review calculation accuracy periodically
- Update documentation as needed
- Plan future enhancements

---

**End of Plan** 📋