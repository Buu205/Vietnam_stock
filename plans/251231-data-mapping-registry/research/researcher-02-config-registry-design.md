# Research Report: Configuration Registry Design for Data Pipelines

**Date:** 2025-12-31
**Research Scope:** Config formats, dependency tracking, mapping structures, scalability patterns
**Sources Consulted:** 15 authoritative sources (2024-2025)

---

## Executive Summary

For data pipeline projects managing 400+ metrics × 19 sectors, **YAML is optimal** for human-readability & versioning, while **Python dataclasses provide type-safe registry implementation**. Three-layer registry pattern (Configuration → Mapping → Resolution) handles dependency tracking via DAG models. Scalability requires metadata-first design with semantic versioning & impact analysis capabilities.

---

## 1. Configuration File Format Analysis

### YAML vs JSON for Pipeline Registry

| Factor | YAML | JSON | Recommendation |
|--------|------|------|---|
| **Readability** | Human-friendly, comments | Strict, verbose | YAML |
| **Performance** | Slower parse | Fast parse | JSON |
| **Security** | Code execution risk | Safe | JSON |
| **Schema Evolution** | Version tags supported | Schema versioning possible | YAML |
| **Ecosystem** | CI/CD standard | APIs, interchange | Both (YAML for config, JSON for storage) |

**Recommendation:** YAML for human-edited configs + JSON for API exchanges.

---

## 2. Registry Architecture Pattern

### Three-Layer Design

```
Layer 1: Configuration (YAML/JSON)
├── pipeline_registry.yaml (source → processor → output)
├── metric_mapping.yaml (metric_id → calculation formula)
└── dashboard_mapping.yaml (output → page → display)

Layer 2: Dataclass Models (Type-safe)
├── PipelineConfig (name, source, processor, outputs)
├── MetricMapping (metric_id, formula, dependencies)
└── DashboardMapping (pipeline → widget → metric)

Layer 3: Registry (Runtime resolution)
├── ConfigRegistry (load YAML → dataclass)
├── DependencyResolver (build DAG from mappings)
└── ImpactAnalyzer (downstream dependency tracking)
```

**Dataclass Example:**

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PipelineMapping:
    pipeline_name: str
    output_file: str
    processors: List[str]
    output_columns: List[str]
    version: str = "1.0"

@dataclass
class DashboardWidget:
    widget_id: str
    pipeline_name: str
    metric: str
    page: str
    refresh_freq: str = "daily"

@dataclass
class RegistryConfig:
    pipelines: Dict[str, PipelineMapping]
    dashboards: Dict[str, DashboardWidget]
    version: str = "1.0"
```

---

## 3. Dependency Tracking via DAG

**Pattern:** Directed Acyclic Graph for dependency visualization.

```
Source Data → Processor 1 → Output A → Dashboard Page 1
            → Processor 2 → Output B → Dashboard Page 2
                                     → Alert Service
```

**Implementation:**
- Load mappings into graph structure
- Validate no circular dependencies
- Track upstream (sources → processor) & downstream (output → consumers)
- Enable impact analysis: "Changing processor 1 affects 3 dashboards"

**Tools Supporting This:**
- Apache Airflow (DAG as code)
- dbt (automatic lineage)
- DVC (data pipeline tracking)

---

## 4. Versioning Strategy

**Semantic Versioning for Registry:**
- `1.0.0` → Initial schema
- `1.1.0` → New optional fields (backward compatible)
- `2.0.0` → Breaking changes

**Metadata Tracking:**
```yaml
version: "2.1.0"
last_updated: "2025-12-31"
author: "data-team"
changes:
  - Added metric: `net_profit_margin`
  - Deprecated: `old_metric` → use `new_metric` instead
```

---

## 5. Scalability Patterns

### Adding New Pipelines (Low friction)
1. Add entry to `pipeline_registry.yaml`
2. Registry auto-loads on startup
3. No code changes required

### Adding New Dashboards (Decoupled)
1. Create entry in `dashboard_mapping.yaml`
2. Reference existing pipelines/metrics
3. Dependency resolver auto-discovers impact

### Validation at Load Time
- Schema validation (JSON Schema / Pydantic)
- Dependency validation (no missing processors)
- Column validation (referenced columns exist in outputs)

---

## 6. Key Recommendations

1. **Use Python dataclasses** with Pydantic for validation
2. **Store config in YAML** (human-readable) + JSON export (API)
3. **Implement dependency resolver** (DAG-based)
4. **Version all configs** (semantic versioning)
5. **Log all changes** (audit trail for impact analysis)
6. **Cache registry at startup** (Streamlit @st.cache_resource)

---

## Unresolved Questions

- Schema evolution strategy for backward compatibility across versions?
- How to handle cross-pipeline metrics that depend on multiple outputs?
- Real-time registry updates (hot-reload) vs. restart-required?

---

## Sources

- [Data Pipeline Architecture Patterns (Alation, 2025)](https://www.alation.com/blog/data-pipeline-architecture-patterns/)
- [DVC Data Pipelines](https://dvc.org/doc/start/data-management/data-pipelines)
- [Data Lineage Tracking (Airbyte, 2025)](https://airbyte.com/data-engineering-resources/track-data-lineage-etl-pipelines/)
- [JSON vs YAML (2026 Guide)](https://dev.to/jsontoall_tools/json-vs-yaml-vs-toml-which-configuration-format-should-you-use-in-2026-1hlb)
- [Python Dataclasses Configuration](https://tech.trueanalytics.ai/posts/dataconf-at-tdg/)
- [dataconf Library](https://github.com/zifeo/dataconf)
