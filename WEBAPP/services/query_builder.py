"""Natural language to MongoDB query builder using LLM."""

from typing import Dict, Any, Optional, List
import json
import logging

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

from .llm_service import get_llm_service
from mongodb.config import get_database
from mongodb.queries import (
    get_latest_metrics,
    get_metrics_by_period,
    get_top_symbols_by_metric,
    get_metric_timeseries,
    compare_symbols_metrics
)

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Build MongoDB queries from natural language."""
    
    def __init__(self, llm_provider: str = 'openai'):
        """
        Initialize query builder.
        
        Args:
            llm_provider: LLM provider ('openai' or 'gemini')
        """
        self.llm = get_llm_service(provider=llm_provider)
        self.db = get_database()
    
    def build_query(self, user_query: str, collection_name: str) -> Dict[str, Any]:
        """
        Build MongoDB query from natural language.
        
        Args:
            user_query: Natural language query
            collection_name: Target collection name
            
        Returns:
            Dict with query parameters
        """
        # Get schema info for context
        schema_info = self._get_schema_info(collection_name)
        
        # Build prompt
        prompt = self._build_prompt(user_query, collection_name, schema_info)
        
        # Call LLM
        messages = [
            {
                'role': 'system',
                'content': 'You are a MongoDB query builder. Convert natural language queries to structured MongoDB query parameters. Return only valid JSON.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        try:
            response = self.llm.chat(messages, temperature=0.3)
            
            # Parse JSON response
            query_params = json.loads(response)
            
            # Validate and normalize
            query_params = self._validate_query(query_params, collection_name)
            
            return query_params
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to simple query
            return self._fallback_query(user_query, collection_name)
        
        except Exception as e:
            logger.error(f"Error building query: {e}")
            return self._fallback_query(user_query, collection_name)
    
    def _get_schema_info(self, collection_name: str) -> Dict[str, Any]:
        """Get schema information for collection."""
        try:
            collection = self.db[collection_name]
            sample = collection.find_one()
            
            if sample:
                return {
                    'fields': list(sample.keys()),
                    'sample': {k: str(v)[:50] for k, v in list(sample.items())[:10]}
                }
        except:
            pass
        
        return {'fields': [], 'sample': {}}
    
    def _build_prompt(self, user_query: str, collection_name: str, schema_info: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        prompt = f"""
Convert the following natural language query to MongoDB query parameters.

User Query: "{user_query}"

Target Collection: {collection_name}

Available Fields: {', '.join(schema_info.get('fields', []))}

Return a JSON object with the following structure:
{{
    "query_type": "symbol" | "latest" | "top" | "timeseries" | "compare",
    "symbol": "string (optional)",
    "symbols": ["array of strings (optional)"],
    "year": integer (optional),
    "quarter": integer 1-4 (optional),
    "metric_field": "string (optional, e.g., 'gross_margin', 'roe')",
    "limit": integer (optional, default 10),
    "start_date": "YYYY-MM-DD (optional)",
    "end_date": "YYYY-MM-DD (optional)",
    "min_value": float (optional),
    "max_value": float (optional)
}}

Query Types:
- "symbol": Get metrics for a specific symbol
- "latest": Get latest metrics (optionally for a symbol)
- "top": Get top symbols by a metric value
- "timeseries": Get time series data for a metric
- "compare": Compare metrics across multiple symbols

Return only the JSON object, no additional text.
"""
        return prompt
    
    def _validate_query(self, query_params: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """Validate and normalize query parameters."""
        # Ensure collection_name is set
        query_params['collection_name'] = collection_name
        
        # Normalize symbol
        if 'symbol' in query_params and query_params['symbol']:
            query_params['symbol'] = str(query_params['symbol']).upper().strip()
        
        # Normalize symbols array
        if 'symbols' in query_params and query_params['symbols']:
            query_params['symbols'] = [str(s).upper().strip() for s in query_params['symbols']]
        
        # Validate query_type
        valid_types = ['symbol', 'latest', 'top', 'timeseries', 'compare']
        if 'query_type' not in query_params or query_params['query_type'] not in valid_types:
            query_params['query_type'] = 'latest'
        
        # Set default limit
        if 'limit' not in query_params:
            query_params['limit'] = 10
        
        return query_params
    
    def _fallback_query(self, user_query: str, collection_name: str) -> Dict[str, Any]:
        """Fallback query if LLM fails."""
        # Simple keyword extraction
        query_lower = user_query.lower()
        
        query_params = {
            'collection_name': collection_name,
            'query_type': 'latest',
            'limit': 10
        }
        
        # Try to extract symbol (common Vietnamese stock symbols)
        common_symbols = ['HPG', 'VCB', 'POW', 'VIC', 'VNM', 'MSN', 'FPT', 'VRE']
        for symbol in common_symbols:
            if symbol.lower() in query_lower:
                query_params['symbol'] = symbol
                query_params['query_type'] = 'symbol'
                break
        
        # Try to extract metric keywords
        metric_keywords = {
            'gross_margin': ['gross margin', 'biên lợi nhuận gộp'],
            'roe': ['roe', 'return on equity', 'lợi nhuận trên vốn'],
            'roa': ['roa', 'return on assets'],
            'ebit_margin': ['ebit margin', 'biên ebit'],
            'net_margin': ['net margin', 'biên lợi nhuận ròng']
        }
        
        for metric, keywords in metric_keywords.items():
            if any(kw in query_lower for kw in keywords):
                query_params['metric_field'] = metric
                if 'top' in query_lower or 'cao nhất' in query_lower or 'best' in query_lower:
                    query_params['query_type'] = 'top'
                break
        
        return query_params


def build_query_from_nl(user_query: str, collection_name: str, llm_provider: str = 'openai') -> Dict[str, Any]:
    """
    Build MongoDB query from natural language.
    
    Args:
        user_query: Natural language query
        collection_name: Target collection name
        llm_provider: LLM provider ('openai' or 'gemini')
        
    Returns:
        Dict with query parameters
    """
    builder = QueryBuilder(llm_provider=llm_provider)
    return builder.build_query(user_query, collection_name)

