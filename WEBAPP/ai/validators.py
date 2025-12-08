"""Query validation for AI-generated queries."""

from typing import Dict, Any, List, Optional


def validate_query_params(query_params: Dict[str, Any], collection_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate query parameters.
    
    Args:
        query_params: Query parameters dict
        collection_name: Target collection name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if 'query_type' not in query_params:
        return False, "query_type is required"
    
    query_type = query_params.get('query_type')
    valid_types = ['symbol', 'latest', 'top', 'timeseries', 'compare']
    
    if query_type not in valid_types:
        return False, f"Invalid query_type: {query_type}. Must be one of {valid_types}"
    
    # Validate based on query type
    if query_type == 'symbol':
        if 'symbol' not in query_params or not query_params['symbol']:
            return False, "symbol is required for query_type 'symbol'"
    
    if query_type == 'top':
        if 'metric_field' not in query_params or not query_params['metric_field']:
            return False, "metric_field is required for query_type 'top'"
    
    if query_type == 'timeseries':
        if 'symbol' not in query_params or not query_params['symbol']:
            return False, "symbol is required for query_type 'timeseries'"
        if 'metric_field' not in query_params or not query_params['metric_field']:
            return False, "metric_field is required for query_type 'timeseries'"
    
    if query_type == 'compare':
        if 'symbols' not in query_params or not query_params['symbols']:
            return False, "symbols array is required for query_type 'compare'"
        if 'metric_field' not in query_params or not query_params['metric_field']:
            return False, "metric_field is required for query_type 'compare'"
    
    # Validate year
    if 'year' in query_params and query_params['year']:
        year = query_params['year']
        if not isinstance(year, int) or year < 2000 or year > 2030:
            return False, f"Invalid year: {year}. Must be between 2000 and 2030"
    
    # Validate quarter
    if 'quarter' in query_params and query_params['quarter']:
        quarter = query_params['quarter']
        if not isinstance(quarter, int) or quarter < 1 or quarter > 4:
            return False, f"Invalid quarter: {quarter}. Must be between 1 and 4"
    
    # Validate limit
    if 'limit' in query_params and query_params['limit']:
        limit = query_params['limit']
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            return False, f"Invalid limit: {limit}. Must be between 1 and 1000"
    
    return True, None


def sanitize_query_params(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and normalize query parameters.
    
    Args:
        query_params: Query parameters dict
        
    Returns:
        Sanitized query parameters
    """
    sanitized = query_params.copy()
    
    # Normalize symbol
    if 'symbol' in sanitized and sanitized['symbol']:
        sanitized['symbol'] = str(sanitized['symbol']).upper().strip()
    
    # Normalize symbols array
    if 'symbols' in sanitized and sanitized['symbols']:
        sanitized['symbols'] = [str(s).upper().strip() for s in sanitized['symbols']]
    
    # Set default limit
    if 'limit' not in sanitized or not sanitized['limit']:
        sanitized['limit'] = 10
    
    # Ensure limit is reasonable
    if sanitized['limit'] > 1000:
        sanitized['limit'] = 1000
    
    return sanitized

