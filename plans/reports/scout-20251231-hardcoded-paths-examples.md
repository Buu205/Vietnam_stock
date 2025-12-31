# Hardcoded Paths - Code Examples & Migration Guide

**Date:** 2025-12-31  
**Purpose:** Provide copy-paste ready migration code for each file type

---

## Example 1: Valuation Calculator Migration

### File: `historical_pe_calculator.py`

**BEFORE (Current):**
```python
from pathlib import Path

# Line 16
PROJECT_ROOT = Path(__file__).resolve().parents[3]

class HistoricalPECalculator:
    def __init__(self):
        # Line 51
        self.base_path = PROJECT_ROOT
        # Lines 56
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'pe' / 'historical'
        
    def load_data(self):
        # Line 119
        file_path = self.base_path / 'DATA' / 'processed' / 'fundamental' / f'{entity}_full.parquet'
```

**AFTER (Proposed):**
```python
from pathlib import Path
from PROCESSORS.core.config.paths import PROCESSED_VALUATION, PROCESSED_FUNDAMENTAL

class HistoricalPECalculator:
    def __init__(self):
        # Direct assignment - no manual path construction
        self.output_path = PROCESSED_VALUATION / 'pe' / 'historical'
        
    def load_data(self):
        # Use PROCESSED_FUNDAMENTAL directly
        file_path = PROCESSED_FUNDAMENTAL / f'{entity}_full.parquet'
```

**Benefits:**
- Remove PROJECT_ROOT dependency
- No manual path construction
- Single source of truth for all paths
- Easier testing and mocking

---

## Example 2: Daily Pipeline Migration

### File: `daily_ta_complete.py`

**BEFORE (Current):**
```python
from pathlib import Path

# Line 29
project_root = Path(__file__).resolve().parents[3]

class DailyTAAnalyzer:
    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        # Line 51 - hardcoded string
        self.ohlcv_path = ohlcv_path or "DATA/raw/ohlcv/OHLCV_mktcap.parquet"
        
    def save_alerts(self):
        # Lines 133, 149, 167 - hardcoded strings
        output_dir = Path("DATA/processed/technical/alerts/daily")
        historical_dir = Path("DATA/processed/technical/alerts/historical")
        output_path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
```

**AFTER (Proposed):**
```python
from pathlib import Path
from PROCESSORS.core.config.paths import RAW_OHLCV, PROCESSED_TECHNICAL

class DailyTAAnalyzer:
    def __init__(self, ohlcv_path: str = None):
        # Use centralized constant as default
        self.ohlcv_path = ohlcv_path or RAW_OHLCV / "OHLCV_mktcap.parquet"
        
    def save_alerts(self):
        # Build paths from centralized PROCESSED_TECHNICAL
        output_dir = PROCESSED_TECHNICAL / "alerts" / "daily"
        historical_dir = PROCESSED_TECHNICAL / "alerts" / "historical"
        output_path = PROCESSED_TECHNICAL / "market_breadth" / "market_breadth_daily.parquet"
```

**Migration Steps:**
1. Replace all `Path("DATA/..."` with constant imports
2. Update parameter defaults to use imported constants
3. Test with same data to verify paths resolve correctly

---

## Example 3: Sector Calculator Migration

### File: `base_aggregator.py`

**BEFORE (Current):**
```python
from pathlib import Path

# Line 43
self.project_root = Path(__file__).resolve().parents[3]

# Line 46
self.sector_output_path = self.processed_path / "sector"
# where self.processed_path is manually constructed from project_root
```

**AFTER (Proposed):**
```python
from PROCESSORS.core.config.paths import PROCESSED_DATA

class BaseAggregator:
    def __init__(self):
        # Direct assignment
        self.sector_output_path = PROCESSED_DATA / "sector"
```

---

## Example 4: Shared Utility Migration

### File: `consistency_checker.py` (Legacy Pattern)

**BEFORE (Current):**
```python
from pathlib import Path

class ConsistencyChecker:
    def __init__(self, data_warehouse_path: str = None):
        """Initialize with optional data warehouse path."""
        # Lines 24-35: Legacy pattern
        if data_warehouse_path is None:
            data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"
        
        self.data_warehouse_path = Path(data_warehouse_path)
```

**AFTER (Proposed):**
```python
from pathlib import Path
from PROCESSORS.core.config.paths import DATA_ROOT

class ConsistencyChecker:
    def __init__(self, data_root: Path = None):
        """Initialize with optional data root path."""
        # Simplified - use centralized constant
        self.data_root = data_root or DATA_ROOT
```

---

## Example 5: API Monitoring Migration

### File: `health_checker.py`

**BEFORE (Current):**
```python
# Lines 102, 164
data_path = self.data_root / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"
```

**AFTER (Proposed):**
```python
from PROCESSORS.core.config.paths import PROCESSED_DATA

# Simpler and more explicit
macro_commodity_path = PROCESSED_DATA / "macro_commodity" / "macro_commodity_unified.parquet"
```

---

## Example 6: Test File Bug Fix

### File: `test_scoring.py` ⚠️ HAS BUG

**BEFORE (Current - BUG):**
```python
# Line 41 - WRONG LEVEL
data_path = Path(__file__).resolve().parents[2] / "DATA" / "processed" / "sector"
# This resolves to: /Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/DATA/...
# INCORRECT! Should be parents[3]
```

**AFTER (Corrected):**
```python
from PROCESSORS.core.config.paths import PROCESSED_DATA

# Correct and centralized
data_path = PROCESSED_DATA / "sector"
```

---

## Batch Migration Checklist

### Step 1: Add Imports (All Files)
```python
# At top of file, after other imports
from PROCESSORS.core.config.paths import (
    PROJECT_ROOT,
    DATA_ROOT,
    RAW_OHLCV,
    RAW_FUNDAMENTAL,
    RAW_COMMODITY,
    RAW_MACRO,
    PROCESSED_DATA,
    PROCESSED_FUNDAMENTAL,
    PROCESSED_TECHNICAL,
    PROCESSED_VALUATION,
    METADATA,
    METRIC_REGISTRY,
    SECTOR_REGISTRY,
)
```

### Step 2: Remove Old Variables
```python
# DELETE THESE
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "DATA"
# etc.
```

### Step 3: Replace Path Strings
```python
# Use Find/Replace patterns:

# Pattern 1: Remove hardcoded strings
Find:    Path("DATA/
Replace: [Import appropriate constant] / 

# Pattern 2: Remove manual construction
Find:    self.base_path / 'DATA' / 'processed' /
Replace: PROCESSED_DATA / 
```

### Step 4: Test
```bash
# Run the script to verify paths still work
python3 path/to/script.py

# Check output directories exist and have correct paths
ls -la DATA/processed/
```

---

## Example Migration Script

For batch migration of multiple files:

```python
#!/usr/bin/env python3
"""
Migrate hardcoded paths to use centralized config.
Usage: python3 migrate_paths.py <file_path>
"""

import sys
import re
from pathlib import Path

REPLACEMENTS = {
    # Pattern -> Replacement
    r'Path\("DATA/raw/ohlcv': 'RAW_OHLCV',
    r'Path\("DATA/processed/technical': 'PROCESSED_TECHNICAL',
    r'Path\("DATA/processed/valuation': 'PROCESSED_VALUATION',
    r'Path\("DATA/processed/fundamental': 'PROCESSED_FUNDAMENTAL',
    r'self\.base_path / \'DATA\' / \'processed\'': 'PROCESSED_DATA',
}

def migrate_file(filepath):
    """Migrate a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Apply replacements
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)
    
    # Only write if changed
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Migrated: {filepath}")
        return True
    else:
        print(f"⏭️  No changes needed: {filepath}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file_path>")
        sys.exit(1)
    
    migrate_file(sys.argv[1])
```

---

## Import Template

Use this as template for all files needing path migration:

```python
"""
Module description here.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Centralized path imports
from PROCESSORS.core.config.paths import (
    PROJECT_ROOT,
    DATA_ROOT,
    RAW_OHLCV,
    RAW_FUNDAMENTAL,
    PROCESSED_DATA,
    PROCESSED_FUNDAMENTAL,
    PROCESSED_TECHNICAL,
    PROCESSED_VALUATION,
    METADATA,
)

# Setup logging
logger = logging.getLogger(__name__)

# === REST OF CODE ===
```

---

## Validation After Migration

Create a test script to verify paths are correct:

```python
"""Verify migrated paths resolve correctly."""

from PROCESSORS.core.config.paths import (
    RAW_OHLCV,
    PROCESSED_TECHNICAL,
    PROCESSED_VALUATION,
)

def verify_paths():
    """Check all paths exist and are accessible."""
    paths_to_check = [
        ("RAW_OHLCV", RAW_OHLCV),
        ("PROCESSED_TECHNICAL", PROCESSED_TECHNICAL),
        ("PROCESSED_VALUATION", PROCESSED_VALUATION),
    ]
    
    for name, path in paths_to_check:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} - NOT FOUND")
            return False
    
    return True

if __name__ == "__main__":
    if verify_paths():
        print("\n✅ All paths verified!")
    else:
        print("\n❌ Some paths failed verification")
```

---

## Common Mistakes to Avoid

### ❌ DON'T: Mix hardcoded and imported paths
```python
# BAD - mixing patterns
output_dir = PROCESSED_TECHNICAL / "alerts"
historical_dir = Path("DATA/processed/technical/alerts/historical")  # Inconsistent!
```

### ✅ DO: Use imported paths consistently
```python
# GOOD - consistent usage
output_dir = PROCESSED_TECHNICAL / "alerts"
historical_dir = PROCESSED_TECHNICAL / "alerts" / "historical"
```

### ❌ DON'T: Keep old PROJECT_ROOT definitions
```python
# BAD - creates confusion
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # Remove this
from PROCESSORS.core.config.paths import PROJECT_ROOT  # Use this
```

### ✅ DO: Import and use
```python
# GOOD - single source
from PROCESSORS.core.config.paths import PROJECT_ROOT
# Use PROJECT_ROOT from import
```

---

## Reference: All Available Constants

From `PROCESSORS/core/config/paths.py`:

```python
# Root level
PROJECT_ROOT          # Project root directory
DATA_ROOT            # DATA directory

# Raw data
RAW_DATA             # DATA/raw/
RAW_OHLCV            # DATA/raw/ohlcv/
RAW_FUNDAMENTAL      # DATA/raw/fundamental/csv/
RAW_COMMODITY        # DATA/raw/commodity/
RAW_MACRO            # DATA/raw/macro/

# Processed data
PROCESSED_DATA       # DATA/processed/
PROCESSED_FUNDAMENTAL # DATA/processed/fundamental/
PROCESSED_TECHNICAL  # DATA/processed/technical/
PROCESSED_VALUATION  # DATA/processed/valuation/

# Metadata
METADATA             # DATA/metadata/
METRIC_REGISTRY      # DATA/metadata/metric_registry.json
SECTOR_REGISTRY      # DATA/metadata/sector_industry_registry.json

# Schemas
SCHEMAS              # DATA/schemas/
SCHEMA_FUNDAMENTAL   # DATA/schemas/fundamental.json
SCHEMA_TECHNICAL     # DATA/schemas/technical.json
SCHEMA_OHLCV         # DATA/schemas/ohlcv.json
```

---

## Pending Implementation

### `get_data_path()` Function

Not yet implemented, but proposed. Once added to `paths.py`, will provide:

```python
# Usage examples after implementation:
get_data_path("raw", "ohlcv")
# → RAW_OHLCV

get_data_path("processed", "valuation", "pe")
# → PROCESSED_VALUATION / "pe"

get_data_path("processed", "technical", "alerts", "daily")
# → PROCESSED_TECHNICAL / "alerts" / "daily"
```

---

**Report Generated:** 2025-12-31  
**Status:** Ready for implementation
