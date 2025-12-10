# Metrics Registry

## Overview

Thư mục này chứa các định nghĩa và registry về metrics cho hệ thống dashboard.

## Files

### `metric_registry.json`

**File chính** - Registry đầy đủ về tất cả các metric codes cho báo cáo tài chính.

- **Nguồn**: Converted from BSC - Mô tả CSDL.xlsx
- **Cấu trúc**: 
  - `entity_types`: COMPANY, BANK, INSURANCE, SECURITY
  - Mỗi entity type có các report types: INCOME, BALANCE, CASHFLOW
  - Mỗi metric có: code, name_vi, name_en, data_type, unit, category, is_calculated, sheet_name, entity_type

**Ví dụ cấu trúc:**
```json
{
  "entity_types": {
    "COMPANY": {
      "INCOME": {
        "CIS_1": {
          "code": "CIS_1",
          "name_vi": "1. Doanh thu bán hàng và cung cấp dịch vụ",
          "name_en": "",
          "data_type": "NUMBER(23,2)",
          "unit": "VND",
          "category": "income",
          "is_calculated": false,
          "sheet_name": "COMPANY_INCOME",
          "entity_type": "COMPANY"
        }
      }
    }
  }
}
```

**Sử dụng:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()
metric_registry = registry.get_metadata("metrics", "metric_registry")

# Access metric info
company_income_metrics = metric_registry["entity_types"]["COMPANY"]["INCOME"]
cis_1_info = company_income_metrics["CIS_1"]
```

### `fundamental_metrics.json`

File reference đến metric_registry.json và giải thích cấu trúc.

### `technical_metrics.json`

Reference đến technical indicator definitions trong `schema_registry/domain/technical/indicators.json`.

### `valuation_metrics.json`

Reference đến valuation metric definitions trong `schema_registry/domain/valuation/metrics.json`.

## Relationship với Schema Registry

- **Detailed Registry**: `metric_registry.json` (file này) - Tất cả metric codes từ BSC
- **Metric Definitions**: `schema_registry/domain/fundamental/metrics.json` - Định nghĩa và formulas cho calculated metrics
- **Metric Definitions**: `schema_registry/domain/technical/indicators.json` - Technical indicators
- **Metric Definitions**: `schema_registry/domain/valuation/metrics.json` - Valuation metrics

## Migration Notes

File `config/metric_registry.json` (file gốc) đã được copy vào đây. File gốc vẫn được giữ để backward compatibility.
