# Data Management Reorganization Plan
# ===================================

## Current Structure Analysis

### Existing Structure
```
DATA/
├── metadata/
│   ├── data_warehouse_schema.json
│   ├── metric_registry.json
│   └── sector_industry_registry.json
└── schemas/
    ├── display/
    ├── master_schema.json
    ├── README.md
    ├── fundamental_calculated_schema.json
    ├── fundamental_schema.json
    ├── ohlcv_data_schema.json
    ├── ohlcv_schema.json
    ├── technical_calculated_schema.json
    └── technical_schema.json
    ├── unified/
    └── valuation_calculated_schema.json
```

### Issues Identified
1. **Scattered schema files** - Multiple similar schemas in different locations
2. **Inconsistent naming** - Some files use different conventions
3. **Mixed data and schema metadata** - Not clearly separated
4. **Hard to maintain** - No single source of truth for schemas

## Proposed New Structure

```
DATA/
├── 1. SCHEMA_REGISTRY/          # All schema definitions
│   ├── core/                   # Core schemas (entities, relations)
│   │   ├── entities.json     # Base entity definitions
│   │   ├── mappings.json     # Field mappings and relationships
│   │   └── types.json        # Data type definitions
│   ├── domain/                 # Domain-specific schemas
│   │   ├── fundamental/     # Fundamental data schemas
│   │   │   ├── metrics.json    # Financial metrics definitions
│   │   │   ├── reports.json    # Financial report structures
│   │   │   └── calculations.json # Calculation formulas
│   │   ├── technical/        # Technical analysis schemas
│   │   │   ├── indicators.json # Technical indicator definitions
│   │   │   ├── signals.json    # Trading signal schemas
│   │   │   └── trends.json     # Trend analysis schemas
│   │   ├── valuation/         # Valuation schemas
│   │   │   ├── metrics.json     # Valuation metric definitions
│   │   │   └── models.json     # Valuation model schemas
│   │   └── unified/           # Unified analysis schemas
│   │       ├── sector.json      # The unified sector schema (existing)
│   │       ├── decisions.json   # Decision-making schemas
│   │       └── insights.json    # AI insights schemas
│   └── display/             # UI/display schemas
│       ├── charts.json          # Chart visualization schemas
│       ├── tables.json          # Table display schemas
│       └── dashboards.json     # Dashboard layout schemas
│
├── 2. METADATA_REGISTRY/       # Metadata and registries
│   ├── sectors/              # Sector classifications and mappings
│   │   ├── industry.json     # ICB industry classifications
│   │   ├── vn_industry.json # Vietnam-specific industries
│   │   └── mappings.json     # Sector mapping tables
│   ├── tickers/              # Ticker information and classifications
│   │   ├── all_tickers.json   # Complete ticker list with metadata
│   │   ├── exchange_mappings.json # Exchange to ticker mappings
│   │   └── sector_mappings.json   # Ticker to sector mappings
│   ├── metrics/              # Metric definitions and mappings
│   │   ├── fundamental_metrics.json # Fundamental metric definitions
│   │   ├── technical_metrics.json # Technical indicator definitions
│   │   └── valuation_metrics.json # Valuation metric definitions
│   └── config/               # Configuration metadata
│       ├── sources.json          # Data source configurations
│       ├── updates.json          # Update schedules and versions
│       └── quality.json         # Data quality standards
│
└── 3. BUSINESS_LOGIC/         # Business logic configurations
    ├── analysis/                # Analysis configurations
    │   ├── fa_analysis.json    # Fundamental analysis settings
    │   ├── ta_analysis.json    # Technical analysis settings
    │   ├── valuation_analysis.json # Valuation analysis settings
    │   └── unified_analysis.json # Unified analysis settings
    ├── decisions/               # Decision-making logic
    │   ├── rules.json          # Trading decision rules
    │   ├── weights.json         # Scoring weight configurations
    │   └── thresholds.json    # Decision threshold settings
    └── alerts/                 # Alert configurations
        ├── rules.json             # Alert triggering rules
        ├── channels.json          # Alert delivery channels
        └── subscriptions.json      # Alert subscriptions
```

## Migration Strategy

### Phase 1: Create New Structure
1. Create the new folder structure `1. SCHEMA_REGISTRY/`
2. Move and consolidate existing schemas
3. Create registry files in `2. METADATA_REGISTRY/`
4. Create business logic configurations

### Phase 2: Update Code References
1. Update all imports to reference new schema locations
2. Update DataPaths configuration to use new structure
3. Test all data loading with new schemas

### Phase 3: Cleanup
1. Remove old scattered schema files
2. Update documentation to reflect new structure
3. Archive old configurations

## Benefits
- **Single Source of Truth**: All schemas in one location
- **Easy Maintenance**: Clear separation of concerns
- **Version Control**: Better schema versioning
- **Extensibility**: Easy to add new schemas
- **Documentation**: Centralized schema documentation

## Next Steps
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Update existing code to use new schema registry
4. Test compatibility with existing data pipelines

## Timeline
- Phase 1: 2-3 days
- Phase 2: 1-2 days  
- Phase 3: 1 day

## Risk Assessment
- **Low Risk**: Changes are organizational only
- **Backward Compatibility**: Maintain old schemas during transition
- **Rollback Plan**: Keep copies of old structure