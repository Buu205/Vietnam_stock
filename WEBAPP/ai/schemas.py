"""MongoDB schema information for AI queries."""

COLLECTION_SCHEMAS = {
    'company_metrics': {
        'description': 'Financial metrics for companies',
        'key_fields': [
            'symbol', 'report_date', 'year', 'quarter',
            'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
            'roe', 'roa', 'eps', 'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi'
        ],
        'metric_fields': [
            'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
            'roe', 'roa', 'eps', 'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi'
        ]
    },
    'bank_metrics': {
        'description': 'Financial metrics for banks',
        'key_fields': [
            'symbol', 'report_date', 'year', 'quarter',
            'roea_ttm', 'roaa_ttm', 'nim_q', 'casa_ratio', 'cir', 'npl_ratio', 'ldr_pure',
            'bvps', 'eps_ttm'
        ],
        'metric_fields': [
            'roea_ttm', 'roaa_ttm', 'nim_q', 'casa_ratio', 'cir', 'npl_ratio', 'ldr_pure',
            'bvps', 'eps_ttm'
        ]
    },
    'insurance_metrics': {
        'description': 'Financial metrics for insurance companies',
        'key_fields': [
            'symbol', 'report_date', 'year', 'quarter'
        ],
        'metric_fields': []
    },
    'security_metrics': {
        'description': 'Financial metrics for securities companies',
        'key_fields': [
            'symbol', 'report_date', 'year', 'quarter'
        ],
        'metric_fields': []
    }
}


def get_collection_schema(collection_name: str) -> dict:
    """
    Get schema information for a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dict with schema information
    """
    return COLLECTION_SCHEMAS.get(collection_name, {
        'description': f'Collection: {collection_name}',
        'key_fields': [],
        'metric_fields': []
    })


def get_available_metrics(collection_name: str) -> list:
    """
    Get available metric fields for a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        List of metric field names
    """
    schema = get_collection_schema(collection_name)
    return schema.get('metric_fields', [])

