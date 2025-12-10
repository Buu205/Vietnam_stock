# AGENTS.md

## Build & Test Commands

**Streamlit App:**
```bash
streamlit run WEBAPP/main.py
```

**Dependencies:**
```bash
pip install -r WEBAPP/requirements.txt
```

**Single Test:**
```bash
python3 test_daily_valuation.py
```

**Data Processing:**
```bash
python3 PROCESSORS/valuation/daily_full_valuation_pipeline.py
```

## Code Style Guidelines

**Naming:**
- Files/modules: `snake_case`
- Classes: `CamelCase` 
- Functions/variables: `snake_case`
- DataFrames: descriptive with `_df` suffix

**Imports:**
- Use absolute imports from project root
- Add project root to path when needed

**Paths (CRITICAL):**
- ALWAYS use canonical v4.0.0 paths: `DATA/raw/`, `DATA/processed/`
- NEVER use deprecated paths: `data_warehouse/`, `calculated_results/`

**Data Processing:**
- Use UnifiedTickerMapper for ticker info
- Load existing calculated results, don't duplicate
- Use transformer functions for pure calculations

**Error Handling:**
- Validate data before calculations (market_cap > 0, earnings notna, etc.)
- Filter symbols appropriately (exclude VIC, VHM, VPB for VN-Index PE)

**Architecture:**
- Follow v4.0.0 canonical architecture
- Update existing documentation, don't create new files
- Use Pydantic models for data validation