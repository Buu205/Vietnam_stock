# 📊 ARCHITECTURE OPTIMIZATION PLAN

**Priority:** 🔴 **HIGH - Professional Structure & MCP Preparation**

**Status:** 📝 Planning Phase | 🔄 Ready for Implementation

**Last Updated:** 2025-12-07

---

## 📋 EXECUTIVE SUMMARY

Dựa trên phân tích cấu trúc hiện tại và yêu cầu của bạn, kế hoạch này đề xuất:

1. **Tái cấu trúc chuyên nghiệp** - Tách biệt rõ ràng giữa dữ liệu và xử lý
2. **Tối ưu hóa công thức** - Phase trước MCP để chuẩn bị dữ liệu parquet
3. **Chuyên nghiệp hóa thư mục** - Đổi tên và tổ chức lại theo chức năng
4. **Roadmap chi tiết** - Từng bước thực hiện

**Timeline:** 2-3 tuần (phải hoàn thành trước phase MCP)

---

## 🔍 PHÂN TÍCH CẤU TRÚC HIỆN TẠI

### Các Vấn Đề Hiện Tại

```
❌ Cấu trúc phân tán
   - Data scattered qua 3 locations (data_warehouse, calculated_results, config)
   - Processing logic scattered (data_processor, technical/indicators)
   - Schemas scattered (3 locations)

❌ Thư mục không rõ chức năng
   - data_warehouse: Chứa cả raw và metadata
   - calculated_results: Chứa cả results và schemas
   - data_processor: Mix nhiều chức năng khác nhau

❌ Không có phân tách Data/Processing
   - Dữ liệu và logic xử lý lẫn lộn
   - Khó maintain và scale
   - Không optimal cho MCP servers
```

### Cấu Trúc Hiện Tại (Sơ Đồ)

```
stock_dashboard/
├── app/                    # Streamlit UI
├── data_warehouse/          # 335MB
│   ├── raw/                # Raw data
│   ├── processed/          # Processed data
│   └── metadata/          # Metadata + schemas
├── calculated_results/      # 834MB (LƯỢNG DATA QUÁ LỚN)
│   ├── schemas/            # Schema files
│   └── [nhiều file data] # Kết quả tính toán
├── data_processor/         # 9.9MB
│   ├── core/              # Core logic
│   ├── fundamental/       # Financial calculations
│   └── technical/        # Technical calculations
└── config/               # Configuration
    └── schemas/          # Schema registry (v2.0.0)
```

### Các Điểm Cần Cải Thiện

1. **Data Locations**: 3 locations → 1 centralized
2. **Processing Logic**: Scattered → Organized by function
3. **Schema Management**: 3 locations → 1 central registry
4. **File Sizes**: calculated_results 834MB → Optimize with Parquet
5. **Naming**: Technical/functional → Professional/function-based

---

## 🏗️ ĐỀ XUẤT CẤU TRÚC MỚI

### Nguyên Tắc Thiết Kế

```
✅ Clear Separation of Concerns
   - DATA = Raw và processed data
   - PROCESSING = Logic tính toán và transform
   - CONFIG = Settings, schemas, metadata
   - RESULTS = Final outputs cho consumption

✅ Functional Organization
   - Mỗi folder có 1 chức năng rõ ràng
   - Tên folder mô tả chính xác chức năng
   - Import paths dễ hiểu

✅ Scalability for MCP
   - Data access optimized for AI agents
   - Clear interfaces between components
   - Consistent schemas and formats
```

### Cấu Trúc Mới Đề Xuất

```
stock_dashboard/
├── 📁 DATA/                                    # ALL DATA IN ONE PLACE
│   ├── raw/                                    # Raw external data
│   │   ├── ohlcv/                             # Price data from APIs
│   │   │   └── OHLCV_mktcap.parquet          (164MB)
│   │   ├── fundamental/                       # Financial statements
│   │   │   └── processed/                     # Material Q3 files
│   │   ├── commodity/                         # Commodity prices
│   │   ├── macro/                             # Interest rates, FX
│   │   └── metadata/                          # Reference data
│   │       ├── metric_registry.json       # 2,099 metrics (752KB)
│   │       ├── sector_industry_registry.json # 457 tickers (94.5KB)
│   │       └── schemas/                    # Data schemas
│   │           ├── fundamental.json
│   │           ├── technical.json
│   │           └── ohlcv.json
│   │
│   ├── processed/                              # Cleaned & standardized
│   │   ├── fundamental/                        # (843MB total)
│   │   │   ├── company/
│   │   │   ├── bank/
│   │   │   ├── insurance/
│   │   │   └── security/
│   │   ├── technical/                          # (791MB)
│   │   │   ├── basic_data.parquet
│   │   │   ├── moving_averages.parquet
│   │   │   └── rsi.parquet
│   │   └── valuation/                          # (31MB)
│   │       ├── stock_pe_pb.parquet
│   │       └── vnindex_pe_daily.parquet
│   │
│   └── archive/                                # Quarterly backups
│       ├── 2025_Q3/                          # Previous quarter data
│       └── 2025_Q4/                          # Current quarter backup
│
├── 📁 PROCESSORS/                              # ALL PROCESSING LOGIC
│   ├── core/                                   # Core utilities
│   │   ├── shared/                            # Base calculators
│   │   ├── formatters/                        # Display formatters
│   │   └── registries/                        # Registry lookups
│   │
│   ├── fundamental/                            # Financial calculations
│   │   ├── formulas/                          # Extracted formulas
│   │   ├── calculators/                       # Base calculator classes
│   │   └── pipelines/                         # Orchestration
│   │
│   ├── technical/                              # Technical analysis
│   │   ├── ohlcv/                            # Price data processing
│   │   ├── indicators/                       # Technical indicators
│   │   └── pipelines/                         # Technical pipelines
│   │
│   ├── valuation/                              # Valuation calculations
│   │   ├── calculators/                       # PE/PB calculators
│   │   └── pipelines/                         # Valuation pipelines
│   │
│   └── forecast/                               # BSC forecast
│
├── 📁 WEBAPP/                                  # STREAMLIT UI
│   ├── main.py                                 # Main app
│   ├── pages/                                  # App pages
│   └── components/                             # Reusable components
│
├── 📁 CONFIG/                                  # GLOBAL CONFIGURATION
│   ├── schemas/                                # Master schema
│   │   ├── master_schema.json             # Global settings
│   │   └── display/                           # UI schemas
│   │       ├── formatting_rules.json
│   │       └── color_theme.json
│   ├── data_sources.json                      # Data source configs
│   └── schema_registry.py                     # Schema registry
│
└── 📁 MCP/                                     # MCP SERVERS
    ├── mongodb/                                # MongoDB MCP server
    └── local/                                  # Local MCP server
```

### Lợi Ích Cấu Trúc Mới

```
✅ Clear Separation
   - Data riêng biệt với processing logic
   - Config tập trung ở 1 nơi
   - Results ready for consumption

✅ Professional Organization
   - Tên folder rõ chức năng
   - Dễ tìm thấy file cần thiết
   - Import paths rõ ràng

✅ MCP Ready
   - Optimized parquet files trong RESULTS/datasets/
   - Clear interfaces trong PROCESSING/engines/
   - Consistent schemas trong CONFIG/schemas/

✅ Scalability
   - Mỗi module có thể phát triển độc lập
   - Dễ thêm data sources mới
   - Tối ưu cho parallel processing
```

---

## 🚀 PHASE 0.3 TRƯỚC MCP: FORMULA OPTIMIZATION & DATA REORGANIZATION

### Mục Tiêu

```
✅ Data Reorganization (Week 1)
   → Tạo cấu trúc DATA/ mới với data/processing tách biệt
   → Di chuyển data từ data_warehouse/ và calculated_results/ → DATA/
   → Giữ lại data_warehouse/metadata/ → DATA/raw/metadata/
   → Cập nhật tất cả import paths

✅ Processing Reorganization (Week 2)
   → Di chuyển data_processor/ → PROCESSORS/
   → Tách biệt formulas (tính toán) và calculators (orchestration)
   → Tạo pipelines cho end-to-end workflows
   → Cập nhật tất cả import paths

✅ Formula Optimization (Week 3)
   → Extract 155+ formulas từ calculator classes
   → Thêm type hints và docstrings chi tiết
   → Tối ưu performance và edge case handling
   → Tạo unit tests cho mỗi formula

✅ Parquet Generation & MCP Preparation (Week 4)
   → Tạo standardized parquet generation pipeline
   → Optimize schema cho query performance
   → Generate validation reports
   → Chuẩn bị cho MCP servers
```

### Implementation Plan

#### Phase 0.3: Formula Optimization (1 tuần)

```python
# 1. Review existing calculators
engines/fundamental_calculator/
├── review_formulas.py           # Audit existing formulas
├── optimize_calculations.py     # Optimize performance
├── validate_results.py          # Compare with reference
└── benchmark_performance.py     # Measure improvements

# 2. Create optimized calculation engine
engines/fundamental_calculator/v2/
├── base_calculator.py           # Optimized base class
├── company_calculator.py        # Company formulas
├── bank_calculator.py          # Bank formulas
├── insurance_calculator.py     # Insurance formulas
└── security_calculator.py      # Security formulas
```

#### Phase 0.4: Parquet Generation (1 tuần)

```python
# 1. Data transformation pipeline
pipelines/data_transformation/
├── source_to_parquet.py        # Convert CSV/JSON → Parquet
├── optimize_schema.py           # Optimize parquet schema
├── add_indexes.py             # Add proper indexing
└── partition_data.py          # Partition large datasets

# 2. Generate final datasets
scripts/generate_datasets.py
├── fundamentals_dataset.py     # Create fundamental parquet
├── technical_dataset.py       # Create technical parquet
├── combined_dataset.py        # Join multiple sources
└── validate_datasets.py       # Quality checks
```

#### Phase 0.5: Dataset Validation (3-4 ngày)

```python
# 1. Validation framework
engines/data_validator/
├── schema_validator.py        # Validate against schemas
├── business_rules.py         # Business logic checks
├── data_quality.py          # Quality metrics
└── anomaly_detection.py     # Find outliers

# 2. Validation reports
reports/validation/
├── dataset_quality.py        # Generate quality reports
├── anomaly_report.py        # Anomaly summaries
└── certification.py        # Final dataset certification
```

### Kết Quả Mong Đợi

```
✅ Optimized Calculation Formulas
   → 50% faster calculation time
   → 100% mathematical accuracy
   → Clear documentation

✅ High-Performance Parquet Datasets
   → 10-100x faster query performance
   → 70% smaller file sizes
   → Proper indexing

✅ MCP-Ready Data
   → Consistent schemas
   → Optimized for AI queries
   → Real-time access capability
```

---

## 📋 DETAILED IMPLEMENTATION ROADMAP

### Tuần 1: Data Reorganization (5 ngày)

#### Ngày 1-2: Create New Structure
```bash
# 1. Create DATA/ directory structure
mkdir -p DATA/{raw,processed,metadata,schemas,archive}
mkdir -p DATA/raw/{ohlcv,fundamental/processed,commodity,macro,news,forecast}
mkdir -p DATA/processed/{fundamental,technical,valuation,commodity,macro}
mkdir -p DATA/processed/fundamental/{company,bank,insurance,security}

# 2. Create PROCESSORS/ directory structure
mkdir -p PROCESSORS/{core,fundamental,technical,valuation,news,forecast}
mkdir -p PROCESSORS/core/{config,shared,formatters,registries}
mkdir -p PROCESSORS/fundamental/{formulas,calculators,pipelines}
mkdir -p PROCESSORS/technical/pipelines
mkdir -p PROCESSORS/valuation/{calculators,pipelines}
```

#### Ngày 3: Move Raw Data
```bash
# Move raw data: data_warehouse/raw/ → DATA/raw/
rsync -av data_warehouse/raw/ DATA/raw/

# Move metadata: data_warehouse/metadata/ → DATA/raw/metadata/
rsync -av data_warehouse/metadata/ DATA/raw/metadata/

# Verify (should match)
du -sh data_warehouse/raw DATA/raw
du -sh data_warehouse/metadata DATA/raw/metadata
```

#### Ngày 4: Move Processed Data
```bash
# Move calculated results: calculated_results/ → DATA/processed/
rsync -av calculated_results/fundamental/ DATA/processed/fundamental/
rsync -av calculated_results/technical/ DATA/processed/technical/
rsync -av calculated_results/valuation/ DATA/processed/valuation/
rsync -av calculated_results/commodity/ DATA/processed/commodity/
rsync -av calculated_results/macro/ DATA/processed/macro/

# Verify total size (should be ~843MB)
du -sh DATA/processed
```

#### Ngày 5: Update Schemas & Paths
```bash
# Consolidate schemas
# Merge: calculated_results/schemas/*.json → DATA/raw/metadata/schemas/
python3 PROCESSORS/core/registries/consolidate_schemas.py

# Create centralized paths configuration
# File: PROCESSORS/core/config/paths.py
```

### Tuần 2: Processing Reorganization (5 ngày)

#### Ngày 1: Move Core Utilities
```bash
# Move: data_processor/core/ → PROCESSORS/core/shared/
rsync -av data_processor/core/ PROCESSORS/core/shared/

# Reorganize into subdirectories
mv PROCESSORS/core/shared/ohlcv_*.py PROCESSORS/core/formatters/
mv PROCESSORS/core/shared/metric_lookup.py PROCESSORS/core/registries/
mv PROCESSORS/core/shared/sector_lookup.py PROCESSORS/core/registries/
mv PROCESSORS/core/shared/build_*.py PROCESSORS/core/registries/
```

#### Ngày 2: Reorganize Fundamental Processors
```bash
# Move: data_processor/fundamental/base/ → PROCESSORS/fundamental/calculators/
rsync -av data_processor/fundamental/base/ PROCESSORS/fundamental/calculators/

# Rename files for clarity
cd PROCESSORS/fundamental/calculators
mv company_financial_calculator.py company_calculator.py
mv bank_financial_calculator.py bank_calculator.py
mv insurance_financial_calculator.py insurance_calculator.py
mv security_financial_calculator.py security_calculator.py
```

#### Ngày 3: Extract Formulas (NEW - Phase 0.3)
```python
# Create: PROCESSORS/fundamental/formulas/company_formulas.py
"""
Extracted formulas from company_calculator.py

Separation of concerns:
- formulas/*.py: Pure calculation logic (testable, auditable)
- calculators/*.py: Data loading, orchestration, output
"""

class CompanyFormulas:
    """Pure calculation functions for company metrics"""

    @staticmethod
    def calculate_roe(net_profit: float, total_equity: float) -> float:
        """ROE = (Net Profit / Total Equity) × 100"""
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return (net_profit / total_equity) * 100

    # ... (all 50+ company formulas extracted)
```

#### Ngày 4: Reorganize Technical Processors
```bash
# Move pipeline files to pipelines/
mv PROCESSORS/technical/daily_*.py PROCESSORS/technical/pipelines/
```

#### Ngày 5: Update All Import Paths
```python
# Create migration script: scripts/update_imports.py
# Updates all imports:
# - data_processor → PROCESSORS
# - data_warehouse/raw → DATA/raw
# - calculated_results → DATA/processed
# - streamlit_app → WEBAPP
```

### Tuần 3: Formula Optimization & Parquet Generation (5 ngày)

#### Ngày 1-2: Audit & Optimize Formulas

**After Optimization:**
```python
# File: PROCESSORS/fundamental/formulas/company_formulas.py
class CompanyFormulas:
    """
    All company calculation formulas.

    Registry mapping:
    - CIS_62: net_profit (Lợi nhuận sau thuế công ty mẹ)
    - CBS_270: total_equity (Vốn chủ sở hữu)
    - CBS_100: total_assets (Tổng tài sản)
    - CIS_11: gross_profit (Lợi nhuận gộp)
    - CIS_02: revenue (Doanh thu thuần)
    """

    @staticmethod
    def calculate_roe(net_profit: float, total_equity: float) -> float:
        """
        Return on Equity (ROE)

        Formula: (Net Profit / Total Equity) × 100
        Unit: Percentage (%)
        Good range: 15-25% (Vietnam market)
        """
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return round((net_profit / total_equity) * 100, 2)
```

#### Ngày 3-4: Create Standardized Parquet Generation Pipeline

```python
# File: PROCESSORS/fundamental/pipelines/quarterly_pipeline.py
"""
Quarterly Fundamental Data Pipeline

Flow:
1. Load raw data from DATA/raw/fundamental/processed/
2. Apply formulas from PROCESSORS/fundamental/formulas/
3. Validate using PROCESSORS/core/shared/data_validator.py
4. Generate parquet files to DATA/processed/fundamental/
5. Create backup in DATA/archive/{year}_Q{quarter}/
6. Generate validation report
"""

class QuarterlyFundamentalPipeline:
    def run(self, quarter: str = "2025-Q4"):
        """
        Run full quarterly update pipeline
        
        Output:
            - DATA/processed/fundamental/company/company_financial_metrics.parquet
            - DATA/archive/2025_Q4/fundamental/
        """
```

#### Ngày 5: Test & Validate
```bash
# Test formula extraction
python3 -m pytest PROCESSORS/fundamental/formulas/tests/

# Test pipeline
python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py --dry-run

# Run full pipeline (if validation passes)
python3 PROCESSORS/fundamental/pipelines/quarterly_pipeline.py --quarter 2025-Q4
```

### Tuần 4: Documentation & Final Integration (5 ngày)

#### Ngày 1-2: Consolidate Documentation
```markdown
# Create: DOCS/INDEX.md (Main entry point)

# Stock Dashboard Documentation

## Quick Start
- [Getting Started](./GETTING_STARTED.md) - 5-minute setup guide
- [Current Status](./CURRENT_STATUS.md) - What's done, what's next

## Development Phases
- [Phase 0.3 Plan](./phases/phase_0.3_plan.md) - Professional structure (THIS PHASE)
- [Phase 1 MCP Plan](./phases/phase_1_mcp_plan.md) - MCP roadmap
```

#### Ngày 3: Update CLAUDE.md
```bash
# Update: CLAUDE.md with new structure
# - Update paths (DATA/, PROCESSORS/, WEBAPP/)
# - Update import examples
# - Update command examples
# - Add formula reference section
```

#### Ngày 4: Create Migration Guide
```markdown
# Create: DOCS/MIGRATION_GUIDE_v2.0_to_v3.0.md

# Migration Guide: v2.0 → v3.0

## Breaking Changes

### Path Changes
- `data_warehouse/raw/` → `DATA/raw/`
- `calculated_results/` → `DATA/processed/`
- `data_processor/` → `PROCESSORS/`
- `streamlit_app/` → `WEBAPP/`

## Migration Steps

1. **Backup current system**
2. **Run migration script**
3. **Update dependencies**
4. **Test**
```

#### Ngày 5: Final Testing & Deployment
```bash
# Full system test
./scripts/test_all.sh

# If all pass, remove old directories
rm -rf data_warehouse/ calculated_results/ data_processor/ streamlit_app/

# Update .gitignore
echo "DATA/processed/" >> .gitignore
echo "DATA/archive/" >> .gitignore
echo "LOGS/" >> .gitignore
```

---

## 🔧 MIGRATION IMPLEMENTATION DETAILS

### Import Path Changes

```python
# BEFORE (v1.0)
from data_processor.fundamental.base.company_financial_calculator import CompanyFinancialCalculator
from data_processor.technical.technical_indicators.technical_processor import TechnicalProcessor
from calculated_results.schemas.fundamental_calculated_schema import fundamental_schema
from data_warehouse.metadata.metric_registry import MetricRegistry

# AFTER (v2.0)
from PROCESSING.engines.fundamental_calculator.company_engine import CompanyEngine
from PROCESSING.engines.technical_processor.technical_engine import TechnicalEngine
from CONFIG.schemas.data.fundamental import fundamental_schema
from CONFIG.registries.metrics import MetricRegistry
```

### Data Access Patterns

```python
# BEFORE (v1.0)
raw_data_path = "data_warehouse/raw/fundamental/material_q3/"
processed_path = "calculated_results/fundamentals/company_fundamentals.parquet"

# AFTER (v2.0)
raw_data_path = "DATA/raw/fundamentals/material_q3/"
processed_path = "RESULTS/datasets/fundamentals/company_fundamentals.parquet"
```

### Configuration Updates

```python
# BEFORE (v1.0)
from config.schema_registry import SchemaRegistry
registry = SchemaRegistry()
schema = registry.get_schema('fundamental')

# AFTER (v2.0)
from CONFIG.registry import ConfigRegistry
registry = ConfigRegistry()
schema = registry.get_schema('data.fundamental')
```

---

## 📊 PERFORMANCE IMPROVEMENTS EXPECTED

### Calculation Performance

```
Metric                  Before         After          Improvement
─────────────────────────────────────────────────────────────
Fundamental Calc Time    45s           20s            -55%
Technical Calc Time     30s           12s            -60%
Memory Usage           2.5GB          1.2GB          -52%
Disk I/O              850MB/s        350MB/s        -59%
```

### Query Performance (Parquet vs CSV)

```
Operation               CSV            Parquet        Improvement
─────────────────────────────────────────────────────────────
Full Table Scan        8.5s           0.9s           -89%
Filter by Column       4.2s           0.3s           -93%
Aggregate Query        12.7s          1.1s           -91%
Multi-Table Join       25.4s          2.8s           -89%
Random Access          6.8s           0.5s           -93%
```

### Storage Efficiency

```
Dataset               CSV Size       Parquet Size   Compression
─────────────────────────────────────────────────────────────
Fundamentals          425MB          95MB           78%
Technical Indicators  210MB          48MB           77%
OHLCV Data           180MB          42MB           77%
Combined Datasets     850MB          180MB          79%
```

---

## 🎯 SUCCESS CRITERIA

### Phase 0.3 Completion Criteria

```
| Metric | Target | Verification |
|--------|--------|--------------|
| **Data Organization** |
| Raw data centralized | 100% in DATA/raw/ | `du -sh DATA/raw/` = 335MB |
| Processed data centralized | 100% in DATA/processed/ | `du -sh DATA/processed/` = 843MB |
| Schemas consolidated | 4 schemas | `ls DATA/raw/metadata/schemas/*.json` |
| **Processing Organization** |
| Formulas extracted | 155+ formulas | Count in formulas/*.py |
| Calculators refactored | 4 entity types | All use formulas/*.py |
| Pipelines created | 3 pipelines | fundamental, technical, valuation |
| **Code Quality** |
| Type hints added | 100% formulas | mypy check |
| Docstrings added | 100% formulas | pydocstyle check |
| Tests passing | 100% | pytest |
| **Documentation** |
| Docs consolidated | Single INDEX.md | All linked from INDEX.md |
| Migration guide | Complete | Tested migration path |
| CLAUDE.md updated | v3.0 structure | Paths, imports, commands |
```

### Technical Success

```
✅ All calculations produce identical results
✅ Performance benchmarks met (50%+ improvement)
✅ All parquet files optimized with proper indexing
✅ MCP servers can access all datasets efficiently
✅ Zero data loss during migration
```

### Operational Success

```
✅ Clear separation between data (DATA/) and processing (PROCESSORS/)
✅ Professional folder structure with functional names
✅ All imports updated and working
✅ Documentation updated for new structure
✅ Team can easily navigate and understand codebase
✅ Formulas extracted and documented for easy audit
✅ Pipelines created for end-to-end workflows
```

### MCP Readiness

```
✅ Consistent schemas across all datasets
✅ Optimized parquet files for fast querying
✅ Clear API interfaces for data access
✅ Proper validation and quality certification
✅ Formula documentation for MCP to explain to users
✅ Clean data paths (DATA/processed/) for MCP access
```

---

## 🚨 RISKS & MITIGATION

### Technical Risks

```
❌ Data Migration Issues
   → Risk: Data loss or corruption during migration
   → Mitigation: Full backup + verification scripts

❌ Import Path Breakages
   → Risk: Code breaks after path changes
   → Mitigation: Automated migration + testing

❌ Performance Regression
   → Risk: New structure slower than expected
   → Mitigation: Benchmarking + optimization
```

### Operational Risks

```
❌ Team Productivity Loss
   → Risk: Team confused by new structure
   → Mitigation: Comprehensive documentation + training

❌ MCP Integration Issues
   → Risk: MCP servers can't access data
   → Mitigation: Early testing + interface standardization

❌ Timeline Delays
   → Risk: Migration takes longer than planned
   → Mitigation: Phased rollout + parallel running
```

---

## 📅 IMPLEMENTATION TIMELINE

### Phase 0.3: Formula Optimization (Week 1)
```
Day 1-2: Planning & Directory Structure
Day 3-4: Formula Review & Optimization
Day 5: Benchmarking & Validation
```

### Phase 0.4: Data Migration & Parquet Generation (Week 2)
```
Day 1-2: Data Migration & Schema Updates
Day 3-4: Parquet Generation & Optimization
Day 5: Performance Testing
```

### Phase 0.5: Final Integration & Testing (Week 3)
```
Day 1-2: Application Updates & Import Changes
Day 3-4: MCP Integration & Testing
Day 5: Documentation & Rollout
```

---

## 📞 NEXT STEPS

### Immediate Actions (This Week)

1. **Review and Approve Plan**
   - Review this optimization plan
   - Approve structure changes
   - Set timeline expectations

2. **Create Migration Scripts**
   - Automated directory restructuring
   - Data migration with validation
   - Import path update scripts

3. **Backup Current System**
   - Full system backup
   - Version control checkpoint
   - Rollback procedure documentation

### Short-term Actions (Week 1-2)

1. **Implement New Structure**
   - Create new directories
   - Migrate data and code
   - Update import paths

2. **Generate Optimized Datasets**
   - Convert to parquet format
   - Add proper indexing
   - Create MCP-ready datasets

3. **Test and Validate**
   - Performance benchmarking
   - Functional testing
   - MCP integration testing

### Long-term Actions (Week 3+)

1. **Documentation and Training**
   - Update all documentation
   - Team training on new structure
   - Best practices guide

2. **Monitor and Optimize**
   - Performance monitoring
   - Fine-tuning as needed
   - Continuous improvement

---

**Document Status:** Ready for Implementation

**Last Updated:** 2025-12-07

**Next Review:** After Phase 0.3 completion (Week 1)