# 🔗 MAPPING INTEGRATION PLAN - Complete System Architecture

**Priority:** 🔴 **CRITICAL - Phase 0.1.5**
**Status:** 📝 **Planning Complete - Ready for Implementation**
**Date:** 2025-12-05

---

## 📋 EXECUTIVE SUMMARY

This document provides a **comprehensive integration plan** showing how `metric_registry.json` and `sector_industry_registry.json` work together to create a unified data access layer for AI agents and calculators.

**Goal:** AI agent calling "ACB" understands:
- ✅ ACB → BANK entity type
- ✅ BANK → uses BIS_*, BBS_* metric codes
- ✅ BANK → applies BankFinancialCalculator
- ✅ BANK → in "Ngân hàng" sector
- ✅ Can read metric definitions from metric_registry.json

---

## 🎯 INTEGRATION ARCHITECTURE

### The Complete Mapping Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED MAPPING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   TICKER     │  ACB (User query)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  sector_industry_registry.json                               │
│  ───────────────────────────────────────────────────────────│
│  "ticker_mapping": {                                         │
│    "ACB": {                                                  │
│      "entity_type": "BANK",        ← Entity Type            │
│      "sector": "Ngân hàng",         ← Sector Name           │
│      "name": "Ngân hàng Á Châu",    ← Full Name            │
│      "exchange": "HOSE"             ← Exchange             │
│    }                                                         │
│  }                                                           │
└─────────┬────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Entity Type: BANK                                           │
│  ──────────────────────────────────────────────────────────│
│  • Calculator Class: BankFinancialCalculator                │
│  • Metric Prefixes: ["BIS_", "BBS_", "BCF_", "BNOT_"]      │
│  • Key Metrics: ["ROE", "ROA", "NIM", "CAR", "NPL"]        │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  metric_registry.json                                        │
│  ──────────────────────────────────────────────────────────│
│  "entity_types": {                                           │
│    "BANK": {                                                 │
│      "INCOME": {                                             │
│        "BIS_1": {                                            │
│          "code": "BIS_1",                                    │
│          "name_vi": "Tổng doanh thu hoạt động",             │
│          "unit": "VND",                                      │
│          "data_type": "NUMBER(23,2)"                        │
│        },                                                    │
│        "BIS_22A": {                                          │
│          "code": "BIS_22A",                                  │
│          "name_vi": "Lợi nhuận sau thuế",                   │
│          ...                                                 │
│        }                                                     │
│      },                                                      │
│      "BALANCE_SHEET": {                                      │
│        "BBS_100": {                                          │
│          "code": "BBS_100",                                  │
│          "name_vi": "Tổng tài sản",                         │
│          ...                                                 │
│        }                                                     │
│      }                                                       │
│    }                                                         │
│  },                                                          │
│  "calculated_metrics": {                                     │
│    "roe": {                                                  │
│      "dependencies": {                                       │
│        "BANK": ["BIS_22A", "BBS_400"]                       │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘

FINAL OUTPUT FOR AI AGENT:
══════════════════════════════════════════════════════════════
{
  "ticker": "ACB",
  "entity_type": "BANK",
  "sector": "Ngân hàng",
  "calculator_class": "BankFinancialCalculator",
  "available_metrics": {
    "BIS_1": "Tổng doanh thu hoạt động",
    "BIS_22A": "Lợi nhuận sau thuế",
    "BBS_100": "Tổng tài sản",
    "BBS_400": "Vốn chủ sở hữu"
  },
  "calculated_metrics": ["ROE", "ROA", "NIM", "CAR"],
  "peer_tickers": ["VCB", "TCB", "MBB", "VPB", ...]
}
```

---

## 🏗️ UNIFIED MAPPER CLASS - Core Integration Component

### Purpose

Create a **single API** that combines:
1. `SectorRegistry` (sector/industry mapping)
2. `MetricRegistry` (metric definitions)
3. Auto-selection logic (calculator, metrics)

### Implementation

**File:** `data_processor/core/unified_mapper.py`

```python
"""
Unified Ticker Mapper - Complete Integration Layer
====================================================

Combines sector_industry_registry.json + metric_registry.json
to provide unified access for AI agents and calculators.

Usage:
    from data_processor.core.unified_mapper import UnifiedTickerMapper

    mapper = UnifiedTickerMapper()
    info = mapper.get_complete_info("ACB")
    # Returns: entity, sector, metrics, calculator, all definitions
"""

from pathlib import Path
import json
from typing import Dict, List, Optional, Set
from data_processor.core.sector_lookup import SectorRegistry
from data_processor.core.metric_lookup import MetricRegistry


class UnifiedTickerMapper:
    """
    Unified mapping interface combining sector and metric registries

    Provides complete ticker information including:
    - Entity type and sector classification
    - Available metric codes and definitions
    - Calculator class selection
    - Peer ticker identification
    """

    def __init__(
        self,
        sector_registry_path: Optional[str] = None,
        metric_registry_path: Optional[str] = None
    ):
        """
        Initialize unified mapper with both registries

        Args:
            sector_registry_path: Path to sector_industry_registry.json
            metric_registry_path: Path to metric_registry.json
        """
        self.sector_registry = SectorRegistry(sector_registry_path)
        self.metric_registry = MetricRegistry(metric_registry_path)

        # Calculator class mapping
        self.calculator_map = {
            "COMPANY": "CompanyFinancialCalculator",
            "BANK": "BankFinancialCalculator",
            "SECURITY": "SecurityFinancialCalculator",
            "INSURANCE": "InsuranceFinancialCalculator"
        }

    def get_complete_info(self, ticker: str) -> Dict:
        """
        Get complete information for a ticker

        This is the MAIN METHOD that AI agents should use.

        Args:
            ticker: Stock ticker (e.g., "ACB", "VCB")

        Returns:
            Complete ticker information dictionary:
            {
                "ticker": str,
                "entity_type": str,
                "sector": str,
                "calculator_class": str,
                "available_metrics": Dict[code, name],
                "calculated_metrics": List[str],
                "peer_tickers": List[str],
                "metric_prefixes": List[str]
            }

        Example:
            >>> mapper = UnifiedTickerMapper()
            >>> info = mapper.get_complete_info("ACB")
            >>> print(info["entity_type"])
            'BANK'
            >>> print(info["available_metrics"]["BIS_22A"])
            'Lợi nhuận sau thuế'
        """
        # Get sector info
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found in sector registry")

        entity_type = ticker_info["entity_type"]
        sector = ticker_info["sector"]

        # Get available metrics for this entity type
        available_metrics = self._get_available_metrics(entity_type)

        # Get calculated metrics that are valid for this entity
        calculated_metrics = self._get_calculated_metrics(entity_type)

        # Get peer tickers (same sector)
        peer_tickers = self.sector_registry.get_peers(ticker)

        # Get metric prefixes
        metric_prefixes = self.sector_registry.get_metric_prefixes(sector)

        return {
            "ticker": ticker,
            "entity_type": entity_type,
            "sector": sector,
            "name": ticker_info.get("name", ""),
            "exchange": ticker_info.get("exchange", ""),
            "calculator_class": self.calculator_map.get(entity_type),
            "available_metrics": available_metrics,
            "calculated_metrics": calculated_metrics,
            "peer_tickers": peer_tickers,
            "metric_prefixes": metric_prefixes
        }

    def _get_available_metrics(self, entity_type: str) -> Dict[str, str]:
        """
        Get all available metric codes and names for entity type

        Args:
            entity_type: "COMPANY", "BANK", "INSURANCE", "SECURITY"

        Returns:
            Dictionary mapping metric codes to Vietnamese names:
            {
                "BIS_1": "Tổng doanh thu hoạt động",
                "BIS_22A": "Lợi nhuận sau thuế",
                ...
            }
        """
        metrics = {}

        # Get all metrics for this entity type from metric registry
        entity_metrics = self.metric_registry.registry["entity_types"].get(entity_type, {})

        for category_name, category_metrics in entity_metrics.items():
            for code, metric_info in category_metrics.items():
                metrics[code] = metric_info["name_vi"]

        return metrics

    def _get_calculated_metrics(self, entity_type: str) -> List[str]:
        """
        Get list of calculated metrics applicable to this entity type

        Args:
            entity_type: "COMPANY", "BANK", "INSURANCE", "SECURITY"

        Returns:
            List of calculated metric names: ["roe", "roa", "eps", ...]
        """
        calculated = []

        calc_metrics = self.metric_registry.registry.get("calculated_metrics", {})

        for metric_name, metric_info in calc_metrics.items():
            if entity_type in metric_info.get("entity_types", []):
                calculated.append(metric_name)

        return calculated

    def get_metric_definition(self, ticker: str, metric_code: str) -> Optional[Dict]:
        """
        Get full metric definition for a specific ticker and metric code

        Args:
            ticker: Stock ticker
            metric_code: Metric code (e.g., "BIS_22A")

        Returns:
            Metric definition dictionary or None if not found

        Example:
            >>> mapper.get_metric_definition("ACB", "BIS_22A")
            {
                "code": "BIS_22A",
                "name_vi": "Lợi nhuận sau thuế",
                "name_en": "Net profit after tax",
                "unit": "VND",
                "data_type": "NUMBER(23,2)",
                "category": "income"
            }
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            return None

        entity_type = ticker_info["entity_type"]
        return self.metric_registry.get_metric(metric_code, entity_type)

    def validate_metric_for_ticker(self, ticker: str, metric_code: str) -> bool:
        """
        Check if a metric code is valid for a ticker's entity type

        Args:
            ticker: Stock ticker
            metric_code: Metric code to validate

        Returns:
            True if metric is valid for this ticker's entity type

        Example:
            >>> mapper.validate_metric_for_ticker("ACB", "BIS_22A")
            True
            >>> mapper.validate_metric_for_ticker("ACB", "CIS_62")
            False  # CIS_62 is for COMPANY, not BANK
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            return False

        entity_type = ticker_info["entity_type"]
        metric = self.metric_registry.get_metric(metric_code, entity_type)

        return metric is not None

    def get_calculator_class(self, ticker: str) -> str:
        """
        Get calculator class name for a ticker

        Args:
            ticker: Stock ticker

        Returns:
            Calculator class name (e.g., "BankFinancialCalculator")

        Example:
            >>> mapper.get_calculator_class("ACB")
            'BankFinancialCalculator'
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found")

        return self.calculator_map.get(ticker_info["entity_type"])

    def search_tickers_with_metric(
        self,
        metric_code: str,
        sector: Optional[str] = None
    ) -> List[str]:
        """
        Find all tickers that have a specific metric available

        Args:
            metric_code: Metric code (e.g., "BIS_22A")
            sector: Optional sector filter

        Returns:
            List of tickers that have this metric

        Example:
            >>> mapper.search_tickers_with_metric("BIS_22A")
            ['ACB', 'VCB', 'TCB', ...]  # All banks

            >>> mapper.search_tickers_with_metric("BIS_22A", "Ngân hàng")
            ['ACB', 'VCB', 'TCB', ...]  # Banks in banking sector
        """
        # Determine which entity type has this metric
        entity_type = None
        for etype in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
            if self.metric_registry.get_metric(metric_code, etype):
                entity_type = etype
                break

        if not entity_type:
            return []

        # Get all tickers for this entity type
        if sector:
            # Filter by sector
            tickers = self.sector_registry.get_tickers_by_sector(sector)
        else:
            # Get all tickers for entity type
            tickers = []
            for sec in self.sector_registry.get_sectors_by_entity(entity_type):
                tickers.extend(self.sector_registry.get_tickers_by_sector(sec))

        return tickers

    def get_peer_comparison_info(self, ticker: str) -> Dict:
        """
        Get complete information for peer comparison

        Args:
            ticker: Stock ticker

        Returns:
            Dictionary with ticker info, peers, and comparison metrics

        Example:
            >>> mapper.get_peer_comparison_info("ACB")
            {
                "ticker": "ACB",
                "sector": "Ngân hàng",
                "peers": ["VCB", "TCB", "MBB", ...],
                "comparison_metrics": ["ROE", "ROA", "NIM", "CAR"],
                "metric_codes": {
                    "ROE": {"dependencies": ["BIS_22A", "BBS_400"]},
                    ...
                }
            }
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found")

        entity_type = ticker_info["entity_type"]
        sector = ticker_info["sector"]

        # Get peers
        peers = self.sector_registry.get_peers(ticker)

        # Get comparison metrics (calculated metrics for this entity)
        comparison_metrics = self._get_calculated_metrics(entity_type)

        # Get metric dependencies
        metric_codes = {}
        calc_metrics = self.metric_registry.registry.get("calculated_metrics", {})
        for metric_name in comparison_metrics:
            if metric_name in calc_metrics:
                metric_info = calc_metrics[metric_name]
                metric_codes[metric_name] = {
                    "dependencies": metric_info["dependencies"].get(entity_type, []),
                    "formula": metric_info.get("formula", ""),
                    "unit": metric_info.get("unit", "")
                }

        return {
            "ticker": ticker,
            "sector": sector,
            "entity_type": entity_type,
            "peers": peers,
            "comparison_metrics": comparison_metrics,
            "metric_codes": metric_codes
        }

    def query_by_natural_language(self, query: str) -> Dict:
        """
        Query system using natural language (AI agent interface)

        Args:
            query: Natural language query

        Returns:
            Query results based on intent

        Example:
            >>> mapper.query_by_natural_language("What sector is ACB?")
            {"ticker": "ACB", "sector": "Ngân hàng", "entity_type": "BANK"}

            >>> mapper.query_by_natural_language("Get all construction stocks")
            {"sector": "Xây dựng và Vật liệu", "tickers": [...]}

            >>> mapper.query_by_natural_language("What calculator for BANK entity?")
            {"entity_type": "BANK", "calculator": "BankFinancialCalculator"}
        """
        query_lower = query.lower()

        # Pattern matching for common queries
        if "what sector" in query_lower or "thuộc ngành" in query_lower:
            # Extract ticker (simple: uppercase words)
            import re
            ticker_match = re.search(r'\b([A-Z]{3})\b', query)
            if ticker_match:
                ticker = ticker_match.group(1)
                ticker_info = self.sector_registry.get_ticker(ticker)
                return {
                    "query_type": "ticker_sector",
                    "ticker": ticker,
                    "sector": ticker_info.get("sector") if ticker_info else None,
                    "entity_type": ticker_info.get("entity_type") if ticker_info else None
                }

        elif "get all" in query_lower or "tất cả cổ phiếu" in query_lower:
            # Search for sector name
            sectors = self.sector_registry.get_all_sectors()
            for sector in sectors:
                if sector.lower() in query_lower:
                    tickers = self.sector_registry.get_tickers_by_sector(sector)
                    return {
                        "query_type": "sector_tickers",
                        "sector": sector,
                        "tickers": tickers,
                        "count": len(tickers)
                    }

        elif "calculator" in query_lower or "calculator class" in query_lower:
            # Extract entity type
            for entity in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
                if entity.lower() in query_lower:
                    return {
                        "query_type": "calculator_class",
                        "entity_type": entity,
                        "calculator": self.calculator_map.get(entity)
                    }

        return {"query_type": "unknown", "message": "Could not parse query"}
```

---

## 💡 USAGE EXAMPLES FOR AI AGENTS

### Example 1: Get Complete Info for a Ticker

```python
from data_processor.core.unified_mapper import UnifiedTickerMapper

mapper = UnifiedTickerMapper()

# AI Query: "Tell me about ACB"
acb_info = mapper.get_complete_info("ACB")

print(f"Ticker: {acb_info['ticker']}")
print(f"Entity Type: {acb_info['entity_type']}")
print(f"Sector: {acb_info['sector']}")
print(f"Calculator: {acb_info['calculator_class']}")
print(f"\nAvailable Metrics ({len(acb_info['available_metrics'])}):")
for code, name in list(acb_info['available_metrics'].items())[:5]:
    print(f"  {code}: {name}")
print(f"\nCalculated Metrics: {acb_info['calculated_metrics']}")
print(f"\nPeer Tickers: {acb_info['peer_tickers'][:10]}")
```

**Output:**
```
Ticker: ACB
Entity Type: BANK
Sector: Ngân hàng
Calculator: BankFinancialCalculator

Available Metrics (150+):
  BIS_1: Tổng doanh thu hoạt động
  BIS_22A: Lợi nhuận sau thuế
  BBS_100: Tổng tài sản
  BBS_400: Vốn chủ sở hữu
  BBS_411: Cổ phiếu phổ thông

Calculated Metrics: ['roe', 'roa', 'eps', 'net_margin']

Peer Tickers: ['VCB', 'TCB', 'MBB', 'VPB', 'STB', ...]
```

---

### Example 2: Validate Metric for Ticker

```python
# AI Query: "Can I use metric BIS_22A for ACB?"
is_valid = mapper.validate_metric_for_ticker("ACB", "BIS_22A")
print(f"BIS_22A valid for ACB: {is_valid}")  # True

# Wrong metric for entity type
is_valid = mapper.validate_metric_for_ticker("ACB", "CIS_62")
print(f"CIS_62 valid for ACB: {is_valid}")  # False (CIS_62 is for COMPANY)
```

---

### Example 3: Get Metric Definition

```python
# AI Query: "What is BIS_22A for ACB?"
metric_def = mapper.get_metric_definition("ACB", "BIS_22A")

print(f"Code: {metric_def['code']}")
print(f"Vietnamese Name: {metric_def['name_vi']}")
print(f"Unit: {metric_def['unit']}")
print(f"Data Type: {metric_def['data_type']}")
```

**Output:**
```
Code: BIS_22A
Vietnamese Name: Lợi nhuận sau thuế
Unit: VND
Data Type: NUMBER(23,2)
```

---

### Example 4: Find All Tickers with Specific Metric

```python
# AI Query: "Which stocks have BIS_22A metric?"
tickers_with_metric = mapper.search_tickers_with_metric("BIS_22A")
print(f"Tickers with BIS_22A: {len(tickers_with_metric)}")
print(f"Sample: {tickers_with_metric[:10]}")
```

**Output:**
```
Tickers with BIS_22A: 24
Sample: ['ACB', 'VCB', 'TCB', 'MBB', 'VPB', 'STB', 'CTG', 'BID', 'TPB', 'MSB']
```

---

### Example 5: Natural Language Query

```python
# AI Query: "What sector is VCB?"
result = mapper.query_by_natural_language("What sector is VCB?")
print(result)
# Output: {"query_type": "ticker_sector", "ticker": "VCB", "sector": "Ngân hàng", "entity_type": "BANK"}

# AI Query: "Get all construction stocks"
result = mapper.query_by_natural_language("Get all construction stocks")
print(result)
# Output: {"query_type": "sector_tickers", "sector": "Xây dựng và Vật liệu", "tickers": [...], "count": 76}

# AI Query: "What calculator for BANK entity?"
result = mapper.query_by_natural_language("What calculator for BANK entity?")
print(result)
# Output: {"query_type": "calculator_class", "entity_type": "BANK", "calculator": "BankFinancialCalculator"}
```

---

## 🔄 INTEGRATION WITH PHASE 2 CALCULATORS

### Auto-Select Calculator Based on Ticker

```python
from data_processor.core.unified_mapper import UnifiedTickerMapper

def calculate_metrics_for_ticker(ticker: str, data_df):
    """
    Auto-select and run calculator for any ticker

    Args:
        ticker: Stock ticker
        data_df: Raw financial data

    Returns:
        Calculated metrics DataFrame
    """
    mapper = UnifiedTickerMapper()

    # Get ticker info
    info = mapper.get_complete_info(ticker)
    entity_type = info["entity_type"]

    # Import calculator dynamically
    if entity_type == "COMPANY":
        from data_processor.fundamental.company.company_financial_calculator_v2 import CompanyFinancialCalculator
        calculator = CompanyFinancialCalculator()
    elif entity_type == "BANK":
        from data_processor.fundamental.bank.bank_financial_calculator_v2 import BankFinancialCalculator
        calculator = BankFinancialCalculator()
    elif entity_type == "INSURANCE":
        from data_processor.fundamental.insurance.insurance_financial_calculator_v2 import InsuranceFinancialCalculator
        calculator = InsuranceFinancialCalculator()
    elif entity_type == "SECURITY":
        from data_processor.fundamental.security.security_financial_calculator_v2 import SecurityFinancialCalculator
        calculator = SecurityFinancialCalculator()

    # Run calculation
    result_df = calculator.calculate(data_df)

    return result_df


# Usage
ticker = "ACB"
raw_data = load_raw_data(ticker)  # From Material Q3/
calculated_metrics = calculate_metrics_for_ticker(ticker, raw_data)
```

---

### Validate Dependencies Before Calculation

```python
def validate_calculation_dependencies(ticker: str, available_codes: Set[str]) -> Dict:
    """
    Check if all required metric codes are available for calculations

    Args:
        ticker: Stock ticker
        available_codes: Set of metric codes in raw data

    Returns:
        Validation result with missing dependencies
    """
    mapper = UnifiedTickerMapper()

    info = mapper.get_complete_info(ticker)
    entity_type = info["entity_type"]

    # Check each calculated metric
    missing_deps = {}

    for calc_metric in info["calculated_metrics"]:
        metric_info = mapper.metric_registry.get_calculated_metric_formula(calc_metric)
        required_codes = set(metric_info["dependencies"].get(entity_type, []))

        missing = required_codes - available_codes
        if missing:
            missing_deps[calc_metric] = list(missing)

    return {
        "ticker": ticker,
        "entity_type": entity_type,
        "valid": len(missing_deps) == 0,
        "missing_dependencies": missing_deps
    }


# Usage
ticker = "ACB"
available_codes = {"BIS_1", "BIS_22A", "BBS_100", "BBS_400", "BBS_411"}

validation = validate_calculation_dependencies(ticker, available_codes)
if not validation["valid"]:
    print(f"Missing dependencies for {ticker}:")
    for metric, missing in validation["missing_dependencies"].items():
        print(f"  {metric}: {missing}")
```

---

## 📊 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                         AI AGENT QUERY                       │
│  "Tell me about ACB and calculate its ROE"                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  UNIFIED TICKER MAPPER                       │
│  mapper.get_complete_info("ACB")                            │
└─────────┬────────────────────────────────┬──────────────────┘
          │                                │
          ▼                                ▼
┌───────────────────────┐      ┌─────────────────────────────┐
│  SECTOR REGISTRY      │      │  METRIC REGISTRY            │
│  ───────────────────  │      │  ──────────────────────────│
│  ACB → BANK          │      │  BANK → BIS_*, BBS_*       │
│  BANK → Ngân hàng    │      │  ROE deps: BIS_22A, BBS_400│
│  Peers: [VCB, TCB..] │      │  Metric definitions        │
└───────────────────────┘      └─────────────────────────────┘
          │                                │
          └────────────────┬───────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE INFO RESPONSE                    │
│  {                                                           │
│    "ticker": "ACB",                                         │
│    "entity_type": "BANK",                                   │
│    "sector": "Ngân hàng",                                   │
│    "calculator_class": "BankFinancialCalculator",          │
│    "available_metrics": {                                   │
│      "BIS_22A": "Lợi nhuận sau thuế",                      │
│      "BBS_400": "Vốn chủ sở hữu",                          │
│      ...                                                    │
│    },                                                       │
│    "calculated_metrics": ["roe", "roa", "eps"],            │
│    "peer_tickers": ["VCB", "TCB", "MBB", ...]             │
│  }                                                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                AUTO-SELECT BANK CALCULATOR                   │
│  from data_processor.fundamental.bank import ...            │
│  calculator = BankFinancialCalculator()                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOAD RAW DATA FOR ACB                      │
│  data_warehouse/Material Q3/BANK_INCOME.csv                 │
│  Filter: SECURITY_CODE = 'ACB'                              │
│  Columns: BIS_1, BIS_22A, BBS_100, BBS_400, ...            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    CALCULATE METRICS                         │
│  roe = (BIS_22A / BBS_400) * 100                           │
│  roa = (BIS_22A / BBS_100) * 100                           │
│  eps = (BIS_22A * 1e9) / (BBS_411 / 10000)                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    RETURN RESULTS TO AI                      │
│  {                                                           │
│    "ticker": "ACB",                                         │
│    "roe": 12.5,                                             │
│    "roa": 1.8,                                              │
│    "eps": 3250,                                             │
│    "peer_comparison": {                                     │
│      "VCB": {"roe": 18.2},                                 │
│      "TCB": {"roe": 15.1},                                 │
│      "sector_median_roe": 14.8                             │
│    }                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ VALIDATION & TESTING STRATEGY

### Test Suite for Unified Mapper

**File:** `data_processor/core/test_unified_mapper.py`

```python
import pytest
from data_processor.core.unified_mapper import UnifiedTickerMapper


class TestUnifiedMapper:
    """Test suite for UnifiedTickerMapper integration"""

    def setup_method(self):
        """Setup mapper instance"""
        self.mapper = UnifiedTickerMapper()

    def test_get_complete_info_bank(self):
        """Test complete info for BANK ticker"""
        info = self.mapper.get_complete_info("ACB")

        assert info["ticker"] == "ACB"
        assert info["entity_type"] == "BANK"
        assert info["sector"] == "Ngân hàng"
        assert info["calculator_class"] == "BankFinancialCalculator"
        assert "BIS_22A" in info["available_metrics"]
        assert "roe" in info["calculated_metrics"]
        assert len(info["peer_tickers"]) > 0

    def test_get_complete_info_company(self):
        """Test complete info for COMPANY ticker"""
        info = self.mapper.get_complete_info("HPG")

        assert info["entity_type"] == "COMPANY"
        assert info["calculator_class"] == "CompanyFinancialCalculator"
        assert "CIS_62" in info["available_metrics"]

    def test_validate_metric_for_ticker(self):
        """Test metric validation"""
        # Valid metric for BANK
        assert self.mapper.validate_metric_for_ticker("ACB", "BIS_22A") == True

        # Invalid metric for BANK (CIS_62 is for COMPANY)
        assert self.mapper.validate_metric_for_ticker("ACB", "CIS_62") == False

    def test_get_metric_definition(self):
        """Test getting metric definition"""
        metric = self.mapper.get_metric_definition("ACB", "BIS_22A")

        assert metric is not None
        assert metric["code"] == "BIS_22A"
        assert "name_vi" in metric
        assert metric["unit"] == "VND"

    def test_search_tickers_with_metric(self):
        """Test finding tickers with specific metric"""
        # All banks should have BIS_22A
        banks = self.mapper.search_tickers_with_metric("BIS_22A")

        assert "ACB" in banks
        assert "VCB" in banks
        assert len(banks) == 24  # Total banks

    def test_get_peer_comparison_info(self):
        """Test peer comparison info"""
        peer_info = self.mapper.get_peer_comparison_info("ACB")

        assert peer_info["ticker"] == "ACB"
        assert peer_info["sector"] == "Ngân hàng"
        assert "VCB" in peer_info["peers"]
        assert "roe" in peer_info["comparison_metrics"]
        assert "BIS_22A" in peer_info["metric_codes"]["roe"]["dependencies"]

    def test_natural_language_query_sector(self):
        """Test natural language query for sector"""
        result = self.mapper.query_by_natural_language("What sector is ACB?")

        assert result["query_type"] == "ticker_sector"
        assert result["ticker"] == "ACB"
        assert result["sector"] == "Ngân hàng"

    def test_natural_language_query_calculator(self):
        """Test natural language query for calculator"""
        result = self.mapper.query_by_natural_language("What calculator for BANK entity?")

        assert result["query_type"] == "calculator_class"
        assert result["entity_type"] == "BANK"
        assert result["calculator"] == "BankFinancialCalculator"

    def test_all_entity_types_have_calculators(self):
        """Test all entity types have calculator classes"""
        for entity in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
            sectors = self.mapper.sector_registry.get_sectors_by_entity(entity)
            assert len(sectors) > 0

            # Get a sample ticker
            sample_ticker = self.mapper.sector_registry.get_tickers_by_sector(sectors[0])[0]
            calculator = self.mapper.get_calculator_class(sample_ticker)

            assert calculator is not None
            assert "Calculator" in calculator
```

**Expected Test Results:**
```
============================================================
TEST RESULTS - Unified Mapper Integration
============================================================
✅ test_get_complete_info_bank ........................ PASS
✅ test_get_complete_info_company ..................... PASS
✅ test_validate_metric_for_ticker .................... PASS
✅ test_get_metric_definition ......................... PASS
✅ test_search_tickers_with_metric .................... PASS
✅ test_get_peer_comparison_info ...................... PASS
✅ test_natural_language_query_sector ................. PASS
✅ test_natural_language_query_calculator ............. PASS
✅ test_all_entity_types_have_calculators ............. PASS
============================================================
9/9 TESTS PASSED ✅
============================================================
```

---

## 🚀 IMPLEMENTATION TIMELINE

### Day 1: Core Integration (6-8 hours)

**Morning (3-4 hours):**
1. Create `unified_mapper.py` with basic structure
2. Implement `get_complete_info()` method
3. Implement `_get_available_metrics()` helper
4. Implement `_get_calculated_metrics()` helper

**Afternoon (3-4 hours):**
5. Implement `validate_metric_for_ticker()` method
6. Implement `get_metric_definition()` method
7. Implement `search_tickers_with_metric()` method
8. Implement `get_peer_comparison_info()` method

---

### Day 2: Testing & Documentation (6-8 hours)

**Morning (3-4 hours):**
1. Create comprehensive test suite (`test_unified_mapper.py`)
2. Run tests and fix issues
3. Ensure 9/9 tests passing

**Afternoon (3-4 hours):**
4. Implement `query_by_natural_language()` method
5. Add usage examples to docstrings
6. Create integration documentation
7. Update architecture documents

---

## 📁 FILE STRUCTURE AFTER IMPLEMENTATION

```
stock_dashboard/
├── data_warehouse/
│   └── metadata/
│       ├── sector_industry_registry.json      ✅ (Phase 0.1.5)
│       └── metric_registry.json               ✅ (Phase 0.1)
│
├── data_processor/core/
│   ├── unified_mapper.py                      ✅ NEW (integration layer)
│   ├── sector_lookup.py                       ✅ (Phase 0.1.5)
│   ├── metric_lookup.py                       ✅ (Phase 0.1)
│   ├── test_unified_mapper.py                 ✅ NEW (test suite)
│   ├── build_sector_registry.py               ✅ (Phase 0.1.5)
│   └── build_metric_registry.py               ✅ (Phase 0.1)
│
└── docs/architecture/
    ├── MAPPING_INTEGRATION_PLAN.md            ✅ THIS FILE
    ├── SECTOR_INDUSTRY_MAPPING.md             ✅ (Phase 0.1.5 spec)
    ├── DATA_STANDARDIZATION.md                ✅ (Foundation plan)
    └── PHASE1_COMPLETION_REPORT.md            ✅ (Phase 0.1 completion)
```

---

## 🎯 SUCCESS CRITERIA

### Integration Completeness
- ✅ UnifiedTickerMapper combines SectorRegistry + MetricRegistry
- ✅ Single API for AI agents: `get_complete_info(ticker)`
- ✅ Automatic calculator selection based on entity type
- ✅ Metric validation for ticker's entity type
- ✅ Natural language query support

### Performance
- ✅ Query response time < 10ms (in-memory lookups)
- ✅ Registry load time < 200ms
- ✅ Support for 457 tickers × 2000+ metrics

### Test Coverage
- ✅ 9/9 integration tests passing
- ✅ All entity types covered (COMPANY, BANK, INSURANCE, SECURITY)
- ✅ Edge cases handled (invalid ticker, wrong metric)

### Documentation
- ✅ Complete API documentation with examples
- ✅ Integration guide for Phase 2 calculators
- ✅ Natural language query examples
- ✅ Data flow diagrams

---

## 🔄 NEXT STEPS AFTER INTEGRATION

### Phase 2: Unified Calculator Refactoring
With the unified mapper in place, Phase 2 can now:
1. Use `mapper.get_calculator_class(ticker)` to auto-select calculators
2. Use `mapper.get_complete_info(ticker)` to get available metrics
3. Validate dependencies with `mapper.validate_metric_for_ticker()`
4. Compare peers using `mapper.get_peer_comparison_info()`

### MCP Agent Integration
MCP agents can now:
1. Query: `mapper.get_complete_info("ACB")` → Full ticker information
2. Query: `mapper.query_by_natural_language("What sector is VCB?")` → Natural language interface
3. Query: `mapper.search_tickers_with_metric("BIS_22A")` → Find tickers by metric

### Dashboard Enhancement
Streamlit app can:
1. Use unified mapper for ticker selection
2. Display sector information alongside metrics
3. Enable peer comparison views
4. Auto-detect calculator requirements

---

## 📝 NOTES

**Key Design Decisions:**
1. **Single Responsibility:** UnifiedTickerMapper focuses only on integration, not calculation
2. **Lazy Loading:** Registries loaded once, cached in memory
3. **Fail-Fast:** Validation methods return False/None instead of raising exceptions
4. **Extensibility:** Easy to add new query methods or entity types

**Trade-offs:**
1. **Memory:** Both registries loaded in memory (~1MB total) → Acceptable for fast queries
2. **Coupling:** Tight coupling between sector and metric registries → Acceptable for integration layer
3. **Performance:** Multiple dictionary lookups per query → Fast enough (<10ms)

---

**Status:** 📝 **Plan Complete - Ready for Implementation**

**Next Action:** Implement `unified_mapper.py` core methods

---

*Last Updated: 2025-12-05*
*Author: Data Standardization Team*
