"""Chat manager for AI chat interface."""

from typing import List, Dict, Any, Optional
import streamlit as st

from .llm_service import get_llm_service
from .query_builder import QueryBuilder
from .response_formatter import format_results_as_table, format_results_as_summary
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

from mongodb.config import get_database
from mongodb.queries import (
    get_latest_metrics,
    get_metrics_by_period,
    get_top_symbols_by_metric,
    get_metric_timeseries,
    compare_symbols_metrics
)


class ChatManager:
    """Manage chat conversation and query execution."""
    
    def __init__(self, collection_name: str = 'company_metrics', llm_provider: str = 'openai'):
        """
        Initialize chat manager.
        
        Args:
            collection_name: Default collection name
            llm_provider: LLM provider ('openai' or 'gemini')
        """
        self.collection_name = collection_name
        self.llm = get_llm_service(provider=llm_provider)
        self.query_builder = QueryBuilder(llm_provider=llm_provider)
        self.db = get_database()
        self.collection = self.db[collection_name]
    
    def process_query(self, user_message: str) -> Dict[str, Any]:
        """
        Process user query and return results.
        
        Args:
            user_message: User's natural language query
            
        Returns:
            Dict with:
                - response: Text response
                - data: Query results (if any)
                - query_type: Type of query executed
        """
        try:
            # Build query from natural language
            query_params = self.query_builder.build_query(user_message, self.collection_name)
            
            # Execute query
            results = self._execute_query(query_params)
            
            # Format response
            response_text = self._format_response(user_message, query_params, results)
            
            return {
                'response': response_text,
                'data': results,
                'query_type': query_params.get('query_type'),
                'query_params': query_params
            }
        
        except Exception as e:
            return {
                'response': f"Sorry, I encountered an error: {str(e)}",
                'data': [],
                'query_type': None,
                'error': str(e)
            }
    
    def _execute_query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute MongoDB query based on parameters."""
        query_type = query_params.get('query_type', 'latest')
        
        if query_type == 'symbol':
            return get_metrics_by_period(
                self.collection,
                symbol=query_params.get('symbol'),
                year=query_params.get('year'),
                quarter=query_params.get('quarter'),
                start_date=query_params.get('start_date'),
                end_date=query_params.get('end_date')
            )
        
        elif query_type == 'latest':
            return get_latest_metrics(
                self.collection,
                symbol=query_params.get('symbol'),
                limit=query_params.get('limit', 10)
            )
        
        elif query_type == 'top':
            return get_top_symbols_by_metric(
                self.collection,
                metric_field=query_params.get('metric_field'),
                limit=query_params.get('limit', 10),
                year=query_params.get('year'),
                quarter=query_params.get('quarter'),
                ascending=query_params.get('ascending', False)
            )
        
        elif query_type == 'timeseries':
            return get_metric_timeseries(
                self.collection,
                symbol=query_params.get('symbol'),
                metric_field=query_params.get('metric_field'),
                start_date=query_params.get('start_date'),
                end_date=query_params.get('end_date')
            )
        
        elif query_type == 'compare':
            return compare_symbols_metrics(
                self.collection,
                symbols=query_params.get('symbols', []),
                metric_field=query_params.get('metric_field'),
                year=query_params.get('year'),
                quarter=query_params.get('quarter')
            )
        
        else:
            return []
    
    def _format_response(self, user_message: str, query_params: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """Format response text using LLM."""
        # Format results summary
        results_summary = format_results_as_summary(
            results,
            metric_field=query_params.get('metric_field')
        )
        
        # Build prompt for LLM to generate natural response
        prompt = f"""
User asked: "{user_message}"

I executed a MongoDB query and got these results:

{results_summary}

Please provide a natural, conversational response in Vietnamese that:
1. Answers the user's question
2. Highlights key findings from the data
3. Is concise and easy to understand

Response (in Vietnamese):
"""
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a helpful financial data assistant. Provide clear, concise responses in Vietnamese about Vietnamese stock market data.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        try:
            response = self.llm.chat(messages, temperature=0.7)
            return response
        except Exception as e:
            # Fallback to simple summary
            return f"Đã tìm thấy {len(results)} kết quả:\n\n{results_summary}"

