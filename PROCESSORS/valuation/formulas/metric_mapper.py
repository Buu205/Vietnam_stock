#!/usr/bin/env python3
"""
Smart Metric Registry Loader
============================
Dynamically loads and queries metric codes from 'config/metadata/metric_registry.json'.
Provides a flexible search API for entity types, categories, sheet names, and keywords.

Features:
- Loads JSON registry on initialization.
- Advanced Search: Query by entity, category, sheet name, and fuzzy name matching.
- Concept Mapping: Maps high-level business concepts (e.g., 'net_income') to specific registry queries.
- Component Support: Handles composite metrics (e.g., Total Debt = Short + Long term).
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Any, Union
import logging

# Setup Logging
logger = logging.getLogger(__name__)

# Project Root Helper
PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PROJECT_ROOT / 'config' / 'metadata' / 'metric_registry.json'
DATA_SOURCES_PATH = PROJECT_ROOT / 'config' / 'data_sources.json'

class MetricRegistryLoader:
    """
    Intelligent loader for metric_registry.json.
    Replaces static mapping with dynamic querying.
    """

    # STANDARD CONCEPTS CONFIGURATION
    STANDARD_CONCEPTS = {
        'net_income': {
            'COMPANY': {'priority': ['CIS_61', 'CIS_60'], 'search': {'name_vi': 'Lợi nhuận sau thuế của cổ đông của công ty mẹ'}},
            'BANK':    {'priority': ['BIS_22A', 'BIS_19'], 'search': {'name_vi': 'Lợi nhuận sau thuế của cổ đông cty mẹ'}},
            'INSURANCE': {'priority': ['IIS_62', 'IIS_60']},
            'SECURITY': {'priority': ['SIS_201', 'SIS_22']}
        },
        'total_equity': {
            'COMPANY': {'priority': ['CBS_400', 'CBS_270'], 'search': {'name_vi': 'VỐN CHỦ SỞ HỮU'}},
            'BANK':    {'priority': ['BBS_501', 'BBS_500'], 'search': {'name_vi': 'VỐN VÀ CÁC QUỸ'}},  # BBS_501 has more data
            'INSURANCE': {'priority': ['IBS_400']},
            'SECURITY': {'priority': ['SBS_400']}
        },
        'cash': {
            'COMPANY': {'priority': ['CBS_110'], 'search': {'name_vi': 'Tiền và các khoản tương đương tiền'}},
            'BANK':    {'priority': ['BBS_100', 'BBS_20']},
            'INSURANCE': {'priority': ['IBS_100']},
            'SECURITY': {'priority': ['SBS_100']}
        },
        'revenue': {
            'COMPANY': {'priority': ['CIS_10'], 'search': {'name_vi': 'Doanh thu thuần'}},
            'BANK':    {'priority': ['BIS_1', 'BIS_20']}, # Thu nhập lãi thuần
            'INSURANCE': {'priority': ['IIS_1']},
            'SECURITY': {'priority': ['SIS_1']}
        },
        'minority_interest': {
            'COMPANY': {'priority': ['CBS_429']}, # Lợi ích cổ đông không kiểm soát
            'BANK':    {'priority': []},
            'INSURANCE': {'priority': []},
            'SECURITY': {'priority': []}
        }
    }
    
    # Composite metrics definition (Metrics made of multiple codes)
    COMPOSITE_METRICS = {
        'total_debt': {
            'COMPANY': ['CBS_320', 'CBS_338'], # Vay ngắn hạn + dài hạn
            'BANK': ['BBS_300', 'BBS_400'],    # Placeholder
        },
        'ebitda': {
            'COMPANY': ['CIS_50', 'CIS_23', 'CNOT_39_3'], # LNTT + Chi phí lãi vay + Khấu hao
            'BANK': [], # Bank EBITDA is complex
        }
    }

    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self.registry_path = registry_path
        self._registry = {} # Stores metric_registry.json content
        self._config_cache = {} # Stores data_sources.json content
        self._load_config() # Load both registry and data sources
        self._cache = {} # Format: cache[concept_key][entity_type] = code

    def _load_config(self):
        """Tải metric_registry.json và data_sources.json"""
        # Load Metric Registry
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    self._registry = json.load(f)
                logger.debug(f"✅ Loaded metric registry from {self.registry_path.name}")
            except Exception as e:
                logger.error(f"❌ Error loading metric registry: {e}")
        else:
            logger.warning(f"Metric Registry not found at {self.registry_path}")
            
        # Load Data Sources
        if DATA_SOURCES_PATH.exists():
            try:
                with open(DATA_SOURCES_PATH, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                logger.debug(f"✅ Loaded data sources config from {DATA_SOURCES_PATH.name}")
            except Exception as e:
                logger.error(f"❌ Error loading Data Sources config: {e}")
        else:
            logger.warning(f"Data Sources config not found at {DATA_SOURCES_PATH}")

    def get_target_frequency(self) -> str:
        """Get the standard TTM frequency code from config (default 'Q')."""
        return self._config_cache.get('valuation_standards', {}).get('frequency', {}).get('target_code', 'Q')

    def get_metric_code(self, concept_key: str, entity_type: str) -> Optional[str]:
        """
        Main API: Get the single best metric code for a concept and entity.
        Uses prioritization logic: Cache -> Explicit Config -> Smart Search.
        """
        entity_type = entity_type.upper()
        
        # 1. Check Cache
        if entity_type in self._cache.get(concept_key, {}):
            return self._cache[concept_key][entity_type]
            
        # 2. Look up Standard Concept Configuration
        concept_conf = self.STANDARD_CONCEPTS.get(concept_key, {}).get(entity_type)
        if not concept_conf:
            return None
        
        # 3. Strategy A: Check Priority List against Registry
        valid_code = None
        priority_codes = concept_conf.get('priority', [])
        
        for code in priority_codes:
            if self._code_exists(code, entity_type):
                valid_code = code
                break
        
        # 4. Strategy B: Fallback to Search if Priority fails
        if not valid_code and 'search' in concept_conf:
            search_params = concept_conf['search']
            found = self.find_metric_code(entity_type=entity_type, **search_params)
            if found:
                valid_code = found
        
        # 5. Default to first in priority even if not found in JSON (Legacy safety)
        if not valid_code and priority_codes:
            valid_code = priority_codes[0]
            
        # Update Cache
        if concept_key not in self._cache:
            self._cache[concept_key] = {}
        self._cache[concept_key][entity_type] = valid_code
        
        return valid_code

    def get_component_codes(self, concept_key: str, entity_type: str) -> List[str]:
        """Get list of codes for composite metrics (e.g. Total Debt)."""
        entity_type = entity_type.upper()
        return self.COMPOSITE_METRICS.get(concept_key, {}).get(entity_type, [])

    def validate_entity_type(self, entity_type: str) -> bool:
        """Validate if entity type is supported."""
        return entity_type.upper() in ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']

    def get_all_codes_for_metric(self, concept_key: str) -> Dict[str, str]:
        """Compatibility method: Returns dict {entity: code} for simple metrics."""
        results = {}
        for entity in ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']:
            code = self.get_metric_code(concept_key, entity)
            if code:
                results[entity] = code
        return results

    def find_metric_code(self, entity_type: str, 
                         name_vi: str = None, 
                         category: str = None, 
                         sheet_name: str = None) -> Optional[str]:
        """
        Advanced Search API: Find a metric code matching criteria.
        """
        entity_data = self._registry.get('entity_types', {}).get(entity_type, {})
        
        # Flatten categories if not specific
        if category:
            search_scope = [entity_data.get(category, {})]
        else:
            search_scope = entity_data.values()
            
        for group in search_scope:
            for code, meta in group.items():
                match = True
                
                # Sheet Name Filter
                if sheet_name and meta.get('sheet_name') != sheet_name:
                    match = False
                
                # Name Keyword Filter (Partial Match)
                if name_vi and name_vi.lower() not in meta.get('name_vi', '').lower():
                    match = False
                    
                if match:
                    return code
        return None

    def _code_exists(self, code: str, entity_type: str) -> bool:
        """Check if a code exists in the loaded registry for that entity."""
        entity_data = self._registry.get('entity_types', {}).get(entity_type, {})
        for category in entity_data.values():
            if code in category:
                return True
        return False
    
# Alias for backward compatibility
ValuationMetricMapper = MetricRegistryLoader

if __name__ == "__main__":
    # Test Run
    logging.basicConfig(level=logging.INFO)
    loader = MetricRegistryLoader()
    
    print("\n--- SMART REGISTRY LOADER TEST ---")
    print(f"Company Net Income: {loader.get_metric_code('net_income', 'COMPANY')}")
    print(f"Bank Equity:        {loader.get_metric_code('total_equity', 'BANK')}")
