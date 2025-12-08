"""Query examples for MongoDB financial metrics collections."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo.collection import Collection
from pymongo import DESCENDING, ASCENDING

from .config import get_database


def get_latest_metrics(
    collection: Collection,
    symbol: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get latest metrics for symbol(s).
    
    Args:
        collection: MongoDB collection
        symbol: Stock symbol (optional, if None returns all)
        limit: Maximum number of records to return
        
    Returns:
        List of latest metric records
    """
    query = {}
    if symbol:
        query['symbol'] = symbol.upper().strip()
    
    cursor = collection.find(query).sort([
        ('report_date', DESCENDING),
        ('year', DESCENDING),
        ('quarter', DESCENDING)
    ]).limit(limit)
    
    return list(cursor)


def get_metrics_by_period(
    collection: Collection,
    symbol: str,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get metrics filtered by period.
    
    Args:
        collection: MongoDB collection
        symbol: Stock symbol
        year: Year filter (optional)
        quarter: Quarter filter (optional)
        start_date: Start date (YYYY-MM-DD format, optional)
        end_date: End date (YYYY-MM-DD format, optional)
        
    Returns:
        List of metric records matching filters
    """
    query = {'symbol': symbol.upper().strip()}
    
    if year:
        query['year'] = year
    if quarter:
        query['quarter'] = quarter
    if start_date:
        query['report_date'] = {'$gte': start_date}
    if end_date:
        if 'report_date' in query:
            query['report_date']['$lte'] = end_date
        else:
            query['report_date'] = {'$lte': end_date}
    
    cursor = collection.find(query).sort([
        ('year', ASCENDING),
        ('quarter', ASCENDING)
    ])
    
    return list(cursor)


def get_metrics_by_value_range(
    collection: Collection,
    metric_field: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    symbol: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get metrics filtered by value range.
    
    Args:
        collection: MongoDB collection
        metric_field: Field name to filter (e.g., 'gross_margin', 'roe')
        min_value: Minimum value (optional)
        max_value: Maximum value (optional)
        symbol: Stock symbol filter (optional)
        
    Returns:
        List of metric records matching value range
    """
    query = {}
    
    if symbol:
        query['symbol'] = symbol.upper().strip()
    
    value_filter = {}
    if min_value is not None:
        value_filter['$gte'] = min_value
    if max_value is not None:
        value_filter['$lte'] = max_value
    
    if value_filter:
        query[metric_field] = value_filter
    
    cursor = collection.find(query).sort([
        ('report_date', DESCENDING)
    ])
    
    return list(cursor)


def get_top_symbols_by_metric(
    collection: Collection,
    metric_field: str,
    limit: int = 10,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    ascending: bool = False
) -> List[Dict[str, Any]]:
    """
    Get top symbols by metric value.
    
    Args:
        collection: MongoDB collection
        metric_field: Field name to rank by (e.g., 'gross_margin', 'roe')
        limit: Number of top symbols to return
        year: Year filter (optional)
        quarter: Quarter filter (optional)
        ascending: If True, sort ascending (lowest first), else descending (highest first)
        
    Returns:
        List of metric records for top symbols
    """
    query = {}
    if year:
        query['year'] = year
    if quarter:
        query['quarter'] = quarter
    
    # Get latest period for each symbol
    pipeline = [
        {'$match': query},
        {'$sort': {'report_date': DESCENDING, 'year': DESCENDING, 'quarter': DESCENDING}},
        {'$group': {
            '_id': '$symbol',
            'latest_doc': {'$first': '$$ROOT'}
        }},
        {'$replaceRoot': {'newRoot': '$latest_doc'}},
        {'$match': {metric_field: {'$exists': True, '$ne': None}}},
        {'$sort': {metric_field: ASCENDING if ascending else DESCENDING}},
        {'$limit': limit}
    ]
    
    cursor = collection.aggregate(pipeline)
    return list(cursor)


def get_metric_timeseries(
    collection: Collection,
    symbol: str,
    metric_field: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get time series data for a specific metric.
    
    Args:
        collection: MongoDB collection
        symbol: Stock symbol
        metric_field: Field name (e.g., 'gross_margin', 'roe')
        start_date: Start date (YYYY-MM-DD format, optional)
        end_date: End date (YYYY-MM-DD format, optional)
        
    Returns:
        List of records with report_date and metric value
    """
    query = {
        'symbol': symbol.upper().strip(),
        metric_field: {'$exists': True, '$ne': None}
    }
    
    if start_date:
        query['report_date'] = {'$gte': start_date}
    if end_date:
        if 'report_date' in query:
            query['report_date']['$lte'] = end_date
        else:
            query['report_date'] = {'$lte': end_date}
    
    projection = {
        'report_date': 1,
        'year': 1,
        'quarter': 1,
        metric_field: 1,
        '_id': 0
    }
    
    cursor = collection.find(query, projection).sort([
        ('year', ASCENDING),
        ('quarter', ASCENDING)
    ])
    
    return list(cursor)


def compare_symbols_metrics(
    collection: Collection,
    symbols: List[str],
    metric_field: str,
    year: Optional[int] = None,
    quarter: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Compare metrics across multiple symbols.
    
    Args:
        collection: MongoDB collection
        symbols: List of stock symbols
        metric_field: Field name to compare
        year: Year filter (optional)
        quarter: Quarter filter (optional)
        
    Returns:
        List of records with symbol and metric value
    """
    symbols_upper = [s.upper().strip() for s in symbols]
    
    query = {
        'symbol': {'$in': symbols_upper},
        metric_field: {'$exists': True, '$ne': None}
    }
    
    if year:
        query['year'] = year
    if quarter:
        query['quarter'] = quarter
    
    # Get latest period for each symbol
    pipeline = [
        {'$match': query},
        {'$sort': {'report_date': DESCENDING, 'year': DESCENDING, 'quarter': DESCENDING}},
        {'$group': {
            '_id': '$symbol',
            'latest_doc': {'$first': '$$ROOT'}
        }},
        {'$replaceRoot': {'newRoot': '$latest_doc'}},
        {'$project': {
            'symbol': 1,
            'report_date': 1,
            'year': 1,
            'quarter': 1,
            metric_field: 1,
            '_id': 0
        }},
        {'$sort': {metric_field: DESCENDING}}
    ]
    
    cursor = collection.aggregate(pipeline)
    return list(cursor)


# Example usage
if __name__ == '__main__':
    from .config import get_database
    
    db = get_database()
    company_collection = db['company_metrics']
    
    # Example 1: Get latest metrics for a symbol
    print("Latest metrics for HPG:")
    latest = get_latest_metrics(company_collection, symbol='HPG', limit=5)
    for record in latest:
        print(f"  {record.get('report_date')} - Q{record.get('quarter')} {record.get('year')}")
    
    # Example 2: Get top symbols by gross margin
    print("\nTop 5 symbols by gross margin:")
    top_margin = get_top_symbols_by_metric(
        company_collection,
        metric_field='gross_margin',
        limit=5
    )
    for record in top_margin:
        print(f"  {record.get('symbol')}: {record.get('gross_margin')}%")
    
    # Example 3: Get time series for a metric
    print("\nGross margin time series for HPG:")
    timeseries = get_metric_timeseries(
        company_collection,
        symbol='HPG',
        metric_field='gross_margin'
    )
    for record in timeseries:
        print(f"  {record.get('report_date')}: {record.get('gross_margin')}%")

