# Research Report: Data Mapping Patterns for Dashboards

**Date:** 2025-12-31 | **Status:** Complete | **Sources:** 3 major searches

## Executive Summary

Data mapping from backend pipelines (Parquet files) → Dashboard UIs requires three layers: **Registry Pattern** for centralized metadata, **Configuration System** for data routing, and **Pipeline-to-Component Binding**. Best practice: segregate data access (backend) from visualization (frontend) using registries as single source of truth. Streamlit + Parquet commonly paired with FastAPI/database backends for production-grade separation.

## Key Findings

### 1. Core Architecture Pattern

**Optimal Stack (2025):**
- Data Layer: Parquet files (columnar, schema-aware)
- Pipeline Layer: Processing scripts → metadata registry
- API/Binding Layer: Centralized configuration + registry
- Frontend: Streamlit (simple) or Dash (complex)

**Key Insight:** Separate concerns rigorously. Supabase/FastAPI/Streamlit pattern isolates DB queries from UI, enabling reusable components.

### 2. Registry Pattern Benefits

| Benefit | Application |
|---------|-------------|
| **Centralized Management** | Single source of truth for metric definitions, data paths, schemas |
| **Decoupling** | Components don't know file locations; query registry instead |
| **Configuration Control** | Update data paths/dependencies without code changes |
| **Dependency Mapping** | Explicit data flow: Pipeline → File → Registry → Component |

### 3. Data Mapping Layers

**Layer 1: Pipeline Registry**
- Track parquet file outputs (location, schema, update frequency)
- Register transformation dependencies (raw → processed → valuation)
- Example: `MetricRegistry.get_metric("PE") → file_path + schema`

**Layer 2: Configuration Store**
- Externalized YAML/JSON defining: data mappings, page-to-file bindings, refresh cadence
- Singleton pattern for consistent access throughout app
- Enables feature flags without code redeploy

**Layer 3: Component-Data Binding**
- Dashboard pages declare data dependencies via config
- Framework fetches data on-demand via registry lookup
- Caching strategy (TTL) defined in registry, not component code

### 4. Real-World Patterns

**Kafka → Spark → Parquet → Streamlit Pipeline:**
- Spark batch jobs transform Parquet files
- FastAPI endpoint exposes aggregated metrics (no direct file access from UI)
- Streamlit dashboard polls API, renders visualizations
- Schema validation at each boundary (pipeline output, API response, component input)

**Multi-Sector Dashboard Mapping:**
- Single registry tracks sector metadata (457 tickers × 19 sectors)
- Page config references registry: `fetch_data("sector.banking.roe")`
- Automatic schema validation ensures column existence before render

### 5. Anti-Patterns to Avoid

- ❌ Hardcoding file paths in dashboard code
- ❌ Multiple metric definitions across codebase
- ❌ Parquet schema assumptions (validate columns before access)
- ❌ Direct DB queries in UI (creates bottleneck, poor scaling)
- ❌ Duplicate calculators (use existing transformers)

## Best Practices

1. **Registry as Metadata Hub**: All metric/sector/ticker lookups via `MetricRegistry.get_metric()`. Prevents hardcoding Vietnamese names.
2. **Externalized Configuration**: YAML files define data mappings; update without code changes.
3. **API Boundary**: Separate frontend from data access via API (FastAPI/REST). Enables caching, rate limiting, auth.
4. **Schema Validation**: Inspect parquet schemas before access. Register expected columns in registry.
5. **Centralized Paths**: Use helper: `get_data_path("processed", "fundamental", "company")` not magic strings.

## Implementation Recommendations

**Quick Pattern:**
```python
# Registry defines everything
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")
# Returns: {path, schema, unit, vietnamese_name, update_freq}

# Page config binds to registry
config = {
  "page": "sector_roe",
  "data_source": "sector.banking.roe",  # Looks up in registry
  "cache_ttl": 3600
}

# Component fetches via registry
data = load_data(config["data_source"])  # Automatic path resolution
```

## Unresolved Questions

1. How to handle schema evolution (new columns in parquet without breaking existing components)?
2. What cache invalidation strategy works best (time-based vs. event-based)?
3. How to define granular data dependencies for complex multi-step pipelines?

## Sources

- [Streamlit Official Docs](https://streamlit.io/)
- [FastAPI + Streamlit Architecture Pattern](https://medium.com/@jv.escorcio/from-data-to-dashboard-building-a-production-ready-app-with-streamlit-fastapi-supabase-and-65e1cf1a1673)
- [Registry Pattern Design Guide](https://java-design-patterns.com/patterns/registry/)
- [Apache Superset Parquet Integration](https://www.restack.io/docs/superset-knowledge-apache-superset-parquet-integration)
- [End-to-End Data Pipeline with Parquet](https://github.com/Xadra-T/End2End-Data-Pipeline)
- [Externalized Configuration Pattern](https://badia-kharroubi.gitbooks.io/microservices-architecture/content/patterns/configuration-patterns/externalized-configuration-store-pattern.html)
