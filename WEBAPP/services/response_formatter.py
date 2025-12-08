"""Format MongoDB query results for display."""

from typing import List, Dict, Any
import pandas as pd


def format_results_as_table(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Format query results as pandas DataFrame.
    
    Args:
        results: List of MongoDB documents
        
    Returns:
        pandas DataFrame
    """
    if not results:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Remove _id column if present
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    
    # Sort columns: put symbol, report_date, year, quarter first
    priority_cols = ['symbol', 'report_date', 'year', 'quarter']
    other_cols = [c for c in df.columns if c not in priority_cols]
    df = df[[c for c in priority_cols if c in df.columns] + other_cols]
    
    return df


def format_results_as_summary(results: List[Dict[str, Any]], metric_field: str = None) -> str:
    """
    Format query results as text summary.
    
    Args:
        results: List of MongoDB documents
        metric_field: Optional metric field to highlight
        
    Returns:
        Formatted text summary
    """
    if not results:
        return "No results found."
    
    summary = f"Found {len(results)} records\n\n"
    
    # Group by symbol if multiple symbols
    if len(set(r.get('symbol', '') for r in results)) > 1:
        summary += "Results by symbol:\n"
        for symbol in sorted(set(r.get('symbol', '') for r in results)):
            symbol_results = [r for r in results if r.get('symbol') == symbol]
            summary += f"\n{symbol} ({len(symbol_results)} records):\n"
            
            for record in symbol_results[:3]:  # Show first 3
                date_str = f"{record.get('report_date', 'N/A')} (Q{record.get('quarter', 'N/A')} {record.get('year', 'N/A')})"
                summary += f"  {date_str}:\n"
                
                if metric_field and metric_field in record:
                    summary += f"    {metric_field}: {record[metric_field]}\n"
                else:
                    # Show key metrics
                    key_metrics = ['gross_margin', 'roe', 'roa', 'ebit_margin', 'net_margin']
                    for metric in key_metrics:
                        if metric in record and record[metric] is not None:
                            summary += f"    {metric}: {record[metric]}\n"
    
    else:
        # Single symbol or no symbol grouping
        for i, record in enumerate(results[:10], 1):  # Show first 10
            symbol = record.get('symbol', 'N/A')
            date_str = f"{record.get('report_date', 'N/A')} (Q{record.get('quarter', 'N/A')} {record.get('year', 'N/A')})"
            summary += f"{i}. {symbol} - {date_str}\n"
            
            if metric_field and metric_field in record:
                summary += f"   {metric_field}: {record[metric_field]}\n"
            else:
                # Show key metrics
                key_metrics = ['gross_margin', 'roe', 'roa', 'ebit_margin', 'net_margin']
                shown = False
                for metric in key_metrics:
                    if metric in record and record[metric] is not None:
                        summary += f"   {metric}: {record[metric]}\n"
                        shown = True
                if not shown:
                    summary += "   (No key metrics available)\n"
            summary += "\n"
        
        if len(results) > 10:
            summary += f"... and {len(results) - 10} more records\n"
    
    return summary


def format_for_chart(results: List[Dict[str, Any]], metric_field: str, date_field: str = 'report_date') -> pd.DataFrame:
    """
    Format results for charting.
    
    Args:
        results: List of MongoDB documents
        metric_field: Metric field to plot
        date_field: Date field to use for x-axis
        
    Returns:
        DataFrame with date and metric columns
    """
    if not results:
        return pd.DataFrame()
    
    chart_data = []
    for record in results:
        chart_data.append({
            'date': record.get(date_field),
            'symbol': record.get('symbol', 'N/A'),
            'value': record.get(metric_field),
            'year': record.get('year'),
            'quarter': record.get('quarter')
        })
    
    df = pd.DataFrame(chart_data)
    
    # Convert date to datetime if possible
    if date_field in df.columns:
        try:
            df[date_field] = pd.to_datetime(df[date_field])
        except:
            pass
    
    return df

