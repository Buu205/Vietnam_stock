# Data Mapping Registry - Clean Architecture Implementation Plan

**Date:** 2025-12-31 | **Status:** ✅ Completed | **Priority:** High

## Problem Statement

Services have hardcoded paths, no explicit mapping: Pipeline → Output → Dashboard → Service.
Adding dashboards requires hunting for paths. No dependency tracking or schema validation.

## Solution: Clean Architecture

```
ENTITIES (Core Domain)
├── DataMapping, PipelineConfig, DashboardConfig dataclasses

USE CASES (Application Logic)
├── DataMappingRegistry, DependencyResolver, PathResolver

INTERFACE ADAPTERS (Controllers/Gateways)
├── Updated Services (BankService, CompanyService...)

FRAMEWORKS & DRIVERS (External)
└── Streamlit Pages, Parquet files
```

## Phases

| Phase | Description | Status | Files |
|-------|-------------|--------|-------|
| 1 | Entities Layer - Core dataclasses | ✅ Done | `config/data_mapping/entities.py` |
| 2 | Registry Layer - YAML config + DataMappingRegistry | ✅ Done | `config/data_mapping/registry.py`, `configs/data_sources.yaml` |
| 3 | Service Integration - Update services to use registry | ✅ Done | 7 services migrated to BaseService |
| 4 | Validation Layer - Schema validation, dependency checks | ✅ Done | `config/data_mapping/validator.py` |

## Implementation Order

1. **Phase 1** (2h): Define dataclasses in `config/data_mapping/entities.py`
2. **Phase 2** (3h): Create registry + YAML configs in `config/data_mapping/`
3. **Phase 3** (4h): Update services to use `DataMappingRegistry`
4. **Phase 4** (2h): Add validation layer, tests

## Key Design Decisions

- **Config Format:** YAML (human-readable) + JSON export (API)
- **Validation:** Pydantic v2 for type safety
- **Singleton:** Registry cached at startup via `@st.cache_resource`
- **Integration:** Works with existing MetricRegistry, SectorRegistry

## File Structure (Target)

```
config/
├── registries/           # Existing (MetricRegistry, SectorRegistry)
├── schema_registry.py    # Existing
└── data_mapping/         # NEW
    ├── __init__.py
    ├── entities.py       # Phase 1: Dataclasses
    ├── registry.py       # Phase 2: DataMappingRegistry
    ├── resolver.py       # Phase 2: PathResolver, DependencyResolver
    ├── validator.py      # Phase 4: Schema validation
    └── configs/
        ├── pipelines.yaml
        ├── dashboards.yaml
        └── services.yaml
```

## Success Criteria

- [x] Zero hardcoded paths in services after Phase 3 ✅
- [x] Adding new dashboard = 1 YAML entry (no code changes) ✅
- [x] Schema validation catches missing columns before render ✅
- [x] Dependency graph shows Pipeline → File → Service → Page mapping ✅

## Integration with Other Plans

- **Technical Dashboard Refactor** (`251225-technical-dashboard-refactor`): Updated to use `TechnicalService`
  - Added 6 new data sources for dashboard tabs
  - Added 7 new service methods for Tab 1-4

## References

- Research: `research/researcher-01-data-mapping-patterns.md`
- Research: `research/researcher-02-config-registry-design.md`
- Existing: `WEBAPP/core/data_paths.py`, `config/registries/`
