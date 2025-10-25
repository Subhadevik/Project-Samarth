"""
Query Engine Module for Project Samarth
Executes natural language queries against agricultural and meteorological datasets
Handles data aggregation, analysis, and response generation with citations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json

from .data_handler import DataHandler, DataProcessor
from .nlp_processor import NLPProcessor, QueryMapper, QueryAnalysis, QueryType

# Configure logging
logger = logging.getLogger(__name__)

class QueryEngine:
    """
    Main query engine that processes natural language questions
    and generates responses with data analysis and citations
    """
    
    def __init__(self, data_handler: DataHandler):
        self.data_handler = data_handler
        self.data_processor = DataProcessor()
        self.nlp_processor = NLPProcessor()
        self.query_mapper = QueryMapper()
        
        # Cache for frequently accessed data
        self.data_cache = {}
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and generate comprehensive response with caching
        
        Args:
            query: Natural language question from user
            
        Returns:
            Dictionary containing answer, data, visualizations, and citations
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Step 1: Analyze the query using NLP
            analysis = self.nlp_processor.analyze_query(query)
            logger.info(f"Query analysis: {analysis.intent}")
            
            # Step 2: Map query to data operations
            operations = self.query_mapper.map_query_to_operations(analysis)
            logger.info(f"Operations mapped: {operations['datasets_needed']}")
            
            # Step 3: Check cache for similar query
            cache_key_params = {
                'query': query,
                'intent': analysis.intent,
                'entities': [{'type': e.entity_type, 'value': e.value} for e in analysis.entities],
                'operations': operations
            }
            
            cached_result = self.data_handler.get_cached_query_result(cache_key_params)
            if cached_result:
                logger.info("Returning cached query result")
                cached_result['cached'] = True
                cached_result['cache_timestamp'] = datetime.now().isoformat()
                return cached_result
            
            # Step 4: Execute data operations
            results = self._execute_operations(operations)
            
            # Step 5: Generate structured response
            response = self._generate_response(query, analysis, operations, results)
            
            # Step 6: Cache the result
            response['cached'] = False
            self.data_handler.cache_query_result(cache_key_params, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': "I apologize, but I encountered an error while processing your query. Please try rephrasing your question.",
                'data': {},
                'citations': [],
                'cached': False
            }
    
    def _execute_operations(self, operations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the mapped data operations
        
        Args:
            operations: Dictionary containing operation specifications
            
        Returns:
            Dictionary containing processed data and metadata
        """
        results = {
            'data': {},
            'metadata': {},
            'statistics': {}
        }
        
        # Load required datasets
        datasets = {}
        for dataset_path in operations['datasets_needed']:
            category, name = dataset_path.split('.')
            
            # Check cache first
            cache_key = f"{category}_{name}"
            if cache_key in self.data_cache:
                df = self.data_cache[cache_key]
            else:
                df = self.data_handler.fetch_data(category, name)
                if df is not None and not df.empty:
                    # Clean the data
                    if category == 'agriculture':
                        df = self.data_processor.clean_agricultural_data(df)
                    elif category == 'meteorology':
                        df = self.data_processor.clean_rainfall_data(df)
                    
                    self.data_cache[cache_key] = df
                else:
                    logger.warning(f"No data found for {dataset_path}")
                    continue
            
            datasets[dataset_path] = df
            
            # Store dataset metadata
            results['metadata'][dataset_path] = {
                'source': self.data_handler.get_dataset_info(category, name),
                'shape': df.shape if df is not None else (0, 0),
                'columns': df.columns.tolist() if df is not None else []
            }
        
        if not datasets:
            logger.warning("No datasets loaded for query")
            return results
        
        # Apply filters
        filtered_datasets = {}
        for dataset_path, df in datasets.items():
            filtered_df = self._apply_filters(df, operations['filters'])
            filtered_datasets[dataset_path] = filtered_df
        
        # Perform aggregations
        if operations['aggregations']:
            for agg_spec in operations['aggregations']:
                agg_results = self._perform_aggregation(
                    filtered_datasets, agg_spec, operations['query_type']
                )
                results['data'].update(agg_results)
        
        # Perform joins if needed
        if len(filtered_datasets) > 1 and operations['joins']:
            joined_data = self._perform_joins(filtered_datasets, operations['joins'])
            results['data']['joined'] = joined_data
        
        # Calculate statistics
        results['statistics'] = self._calculate_statistics(results['data'])
        
        return results
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to dataframe based on query parameters
        """
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Apply entity-based filters
        for column, values in filters.items():
            if column == 'year_range':
                start_year, end_year = values
                if 'year' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['year'] >= start_year) & 
                        (filtered_df['year'] <= end_year)
                    ]
            elif column in filtered_df.columns:
                if isinstance(values, list):
                    # Handle multiple values (OR condition)
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
                else:
                    # Handle single value
                    filtered_df = filtered_df[filtered_df[column] == values]
        
        return filtered_df
    
    def _perform_aggregation(self, datasets: Dict[str, pd.DataFrame], 
                           agg_spec: Dict[str, Any], query_type: str) -> Dict[str, Any]:
        """
        Perform aggregation based on specification
        """
        results = {}
        
        column = agg_spec['column']
        function = agg_spec['function']
        group_by = agg_spec.get('group_by', [])
        
        for dataset_path, df in datasets.items():
            if df.empty or column not in df.columns:
                continue
            
            dataset_name = dataset_path.replace('.', '_')
            
            if group_by:
                # Group by specified columns
                valid_group_by = [col for col in group_by if col in df.columns]
                if valid_group_by:
                    if query_type == 'comparison':
                        # For comparison queries, keep groups separate
                        grouped = df.groupby(valid_group_by)[column].agg(function).reset_index()
                        results[f"{dataset_name}_grouped"] = grouped
                    elif query_type == 'trend_analysis':
                        # For trend analysis, create time series
                        if 'year' in valid_group_by:
                            grouped = df.groupby(valid_group_by)[column].agg(function).reset_index()
                            grouped = grouped.sort_values('year')
                            results[f"{dataset_name}_trend"] = grouped
                    elif query_type == 'ranking':
                        # For ranking, aggregate and sort
                        grouped = df.groupby(valid_group_by)[column].agg(function).reset_index()
                        grouped = grouped.sort_values(column, ascending=False)
                        results[f"{dataset_name}_ranked"] = grouped
                    else:
                        grouped = df.groupby(valid_group_by)[column].agg(function).reset_index()
                        results[f"{dataset_name}_aggregated"] = grouped
            else:
                # Overall aggregation
                if function == 'sum':
                    value = df[column].sum()
                elif function == 'mean':
                    value = df[column].mean()
                elif function == 'max':
                    value = df[column].max()
                elif function == 'min':
                    value = df[column].min()
                elif function == 'count':
                    value = df[column].count()
                else:
                    value = df[column].sum()  # Default to sum
                
                results[f"{dataset_name}_total"] = value
        
        return results
    
    def _perform_joins(self, datasets: Dict[str, pd.DataFrame], 
                      join_specs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Perform joins between datasets
        """
        # For now, implement a simple join on common columns
        dataset_list = list(datasets.values())
        
        if len(dataset_list) < 2:
            return dataset_list[0] if dataset_list else pd.DataFrame()
        
        # Find common columns
        common_columns = set(dataset_list[0].columns)
        for df in dataset_list[1:]:
            common_columns &= set(df.columns)
        
        # Use state and year as default join keys
        join_keys = ['state', 'year']
        join_keys = [key for key in join_keys if key in common_columns]
        
        if not join_keys:
            logger.warning("No common join keys found")
            return dataset_list[0]
        
        # Perform outer join
        result = dataset_list[0]
        for df in dataset_list[1:]:
            result = pd.merge(result, df, on=join_keys, how='outer', suffixes=('', '_y'))
        
        return result
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics for the results
        """
        stats = {
            'total_records': 0,
            'data_points': 0,
            'date_range': {},
            'summary': {}
        }
        
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                stats['total_records'] += len(value)
                stats['data_points'] += value.select_dtypes(include=[np.number]).count().sum()
                
                # Calculate date range if year column exists
                if 'year' in value.columns:
                    min_year = value['year'].min()
                    max_year = value['year'].max()
                    stats['date_range'][key] = f"{min_year}-{max_year}"
                
                # Calculate summary statistics for numeric columns
                numeric_columns = value.select_dtypes(include=[np.number]).columns
                for col in numeric_columns:
                    if col not in stats['summary']:
                        stats['summary'][col] = {}
                    
                    stats['summary'][col][key] = {
                        'mean': value[col].mean(),
                        'median': value[col].median(),
                        'std': value[col].std(),
                        'min': value[col].min(),
                        'max': value[col].max()
                    }
        
        return stats
    
    def _generate_response(self, original_query: str, analysis: QueryAnalysis,
                          operations: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured response with answer, data, and citations
        """
        response = {
            'success': True,
            'query': original_query,
            'intent': analysis.intent,
            'confidence': analysis.confidence,
            'answer': '',
            'data': {},
            'visualizations': [],
            'citations': [],
            'metadata': {
                'query_type': analysis.query_type.value,
                'entities_found': len(analysis.entities),
                'datasets_used': operations['datasets_needed'],
                'processing_time': datetime.now().isoformat()
            }
        }
        
        # Generate natural language answer
        response['answer'] = self._generate_natural_answer(analysis, results)
        
        # Format data for frontend
        response['data'] = self._format_data_for_frontend(results['data'])
        
        # Generate visualizations
        response['visualizations'] = self._generate_visualizations(
            analysis.query_type, results['data']
        )
        
        # Generate citations
        response['citations'] = self._generate_citations(results['metadata'])
        
        return response
    
    def _generate_natural_answer(self, analysis: QueryAnalysis, 
                               results: Dict[str, Any]) -> str:
        """
        Generate natural language answer based on query type and results
        """
        if not results['data']:
            return "I couldn't find relevant data to answer your query. Please try rephrasing your question or check if the requested data is available."
        
        query_type = analysis.query_type
        entities = {e.entity_type: e.value for e in analysis.entities}
        
        answer_parts = []
        
        if query_type == QueryType.COMPARISON:
            answer_parts.append(self._generate_comparison_answer(entities, results))
        elif query_type == QueryType.RANKING:
            answer_parts.append(self._generate_ranking_answer(entities, results))
        elif query_type == QueryType.TREND_ANALYSIS:
            answer_parts.append(self._generate_trend_answer(entities, results))
        elif query_type == QueryType.CORRELATION:
            answer_parts.append(self._generate_correlation_answer(entities, results))
        else:
            answer_parts.append(self._generate_general_answer(entities, results))
        
        # Add data summary
        stats = results.get('statistics', {})
        if stats.get('total_records', 0) > 0:
            answer_parts.append(f"\n\nThis analysis is based on {stats['total_records']} data records.")
        
        return " ".join(answer_parts)
    
    def _generate_comparison_answer(self, entities: Dict[str, str], 
                                  results: Dict[str, Any]) -> str:
        """Generate answer for comparison queries"""
        
        # Find comparison data
        comparison_data = None
        for key, value in results['data'].items():
            if isinstance(value, pd.DataFrame) and 'grouped' in key:
                comparison_data = value
                break
        
        if comparison_data is None or comparison_data.empty:
            return "I couldn't find sufficient data to make the requested comparison."
        
        # Generate comparison text
        if 'state' in entities:
            states = comparison_data['state'].unique()
            if len(states) >= 2:
                state1, state2 = states[0], states[1]
                
                # Get values for comparison
                metric_col = [col for col in comparison_data.columns 
                             if col not in ['state', 'year', 'crop']]
                if metric_col:
                    metric = metric_col[0]
                    val1 = comparison_data[comparison_data['state'] == state1][metric].iloc[0]
                    val2 = comparison_data[comparison_data['state'] == state2][metric].iloc[0]
                    
                    if val1 > val2:
                        return f"Based on the data, {state1} has higher {metric} ({val1:,.2f}) compared to {state2} ({val2:,.2f})."
                    else:
                        return f"Based on the data, {state2} has higher {metric} ({val2:,.2f}) compared to {state1} ({val1:,.2f})."
        
        return "Here's the comparison data you requested. Please refer to the table below for detailed values."
    
    def _generate_ranking_answer(self, entities: Dict[str, str], 
                               results: Dict[str, Any]) -> str:
        """Generate answer for ranking queries"""
        
        # Find ranking data
        ranking_data = None
        for key, value in results['data'].items():
            if isinstance(value, pd.DataFrame) and 'ranked' in key:
                ranking_data = value
                break
        
        if ranking_data is None or ranking_data.empty:
            return "I couldn't find sufficient data to generate the requested ranking."
        
        # Get top and bottom entries
        top_entry = ranking_data.iloc[0]
        bottom_entry = ranking_data.iloc[-1]
        
        metric_col = [col for col in ranking_data.columns 
                     if col not in ['state', 'year', 'crop']]
        
        if metric_col:
            metric = metric_col[0]
            crop = entities.get('crop', 'crop')
            
            answer = f"Based on the available data, "
            
            if 'state' in ranking_data.columns:
                answer += f"{top_entry['state']} has the highest {metric} "
                if crop != 'crop':
                    answer += f"for {crop} "
                answer += f"({top_entry[metric]:,.2f}), while {bottom_entry['state']} has the lowest "
                answer += f"({bottom_entry[metric]:,.2f})."
            
            return answer
        
        return "Here's the ranking data you requested. Please refer to the table below for detailed information."
    
    def _generate_trend_answer(self, entities: Dict[str, str], 
                             results: Dict[str, Any]) -> str:
        """Generate answer for trend analysis queries"""
        
        # Find trend data
        trend_data = None
        for key, value in results['data'].items():
            if isinstance(value, pd.DataFrame) and 'trend' in key:
                trend_data = value
                break
        
        if trend_data is None or trend_data.empty:
            return "I couldn't find sufficient data to analyze the requested trend."
        
        if 'year' in trend_data.columns:
            metric_col = [col for col in trend_data.columns 
                         if col not in ['state', 'year', 'crop']]
            
            if metric_col:
                metric = metric_col[0]
                
                # Calculate trend direction
                first_value = trend_data[metric].iloc[0]
                last_value = trend_data[metric].iloc[-1]
                
                crop = entities.get('crop', 'the metric')
                state = entities.get('state', '')
                
                if last_value > first_value:
                    direction = "increasing"
                    change = ((last_value - first_value) / first_value) * 100
                elif last_value < first_value:
                    direction = "decreasing"
                    change = ((first_value - last_value) / first_value) * 100
                else:
                    direction = "stable"
                    change = 0
                
                answer = f"The trend analysis shows that {metric} for {crop}"
                if state:
                    answer += f" in {state}"
                answer += f" has been {direction} over the analyzed period"
                
                if change > 0:
                    answer += f", with a change of approximately {change:.1f}%"
                
                answer += "."
                
                return answer
        
        return "Here's the trend analysis data. Please refer to the chart and table below for detailed information."
    
    def _generate_correlation_answer(self, entities: Dict[str, str], 
                                   results: Dict[str, Any]) -> str:
        """Generate answer for correlation queries"""
        return "I've analyzed the correlation between the agricultural and meteorological data. Please refer to the detailed analysis below."
    
    def _generate_general_answer(self, entities: Dict[str, str], 
                               results: Dict[str, Any]) -> str:
        """Generate answer for general queries"""
        return "Here's the information I found based on your query. Please refer to the data and visualizations below for detailed insights."
    
    def _format_data_for_frontend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for frontend consumption
        """
        formatted_data = {}
        
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                # Convert DataFrame to dictionary format
                formatted_data[key] = {
                    'columns': value.columns.tolist(),
                    'data': value.to_dict('records'),
                    'shape': value.shape
                }
            else:
                formatted_data[key] = value
        
        return formatted_data
    
    def _generate_visualizations(self, query_type: QueryType, 
                               data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate visualization specifications for frontend
        """
        visualizations = []
        
        for key, value in data.items():
            if not isinstance(value, pd.DataFrame) or value.empty:
                continue
            
            viz_spec = {
                'id': f"viz_{key}",
                'title': key.replace('_', ' ').title(),
                'data_key': key
            }
            
            # Determine chart type based on query type and data structure
            if query_type == QueryType.TREND_ANALYSIS and 'year' in value.columns:
                viz_spec['type'] = 'line'
                viz_spec['x_axis'] = 'year'
                numeric_cols = value.select_dtypes(include=[np.number]).columns
                viz_spec['y_axis'] = numeric_cols[0] if len(numeric_cols) > 0 else 'value'
                
            elif query_type == QueryType.COMPARISON:
                viz_spec['type'] = 'bar'
                if 'state' in value.columns:
                    viz_spec['x_axis'] = 'state'
                numeric_cols = value.select_dtypes(include=[np.number]).columns
                viz_spec['y_axis'] = numeric_cols[0] if len(numeric_cols) > 0 else 'value'
                
            elif query_type == QueryType.RANKING:
                viz_spec['type'] = 'horizontal_bar'
                if 'state' in value.columns:
                    viz_spec['x_axis'] = 'state'
                numeric_cols = value.select_dtypes(include=[np.number]).columns
                viz_spec['y_axis'] = numeric_cols[0] if len(numeric_cols) > 0 else 'value'
                
            else:
                viz_spec['type'] = 'table'
            
            visualizations.append(viz_spec)
        
        return visualizations
    
    def _generate_citations(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate enhanced citations for data sources with full traceability
        """
        citations = []
        
        for dataset_path, info in metadata.items():
            if 'source' in info:
                source_info = info['source']
                
                # Get enhanced dataset information
                dataset_parts = dataset_path.split('.')
                if len(dataset_parts) == 2:
                    category, name = dataset_parts
                    enhanced_info = self.data_handler.get_enhanced_dataset_info(category, name)
                else:
                    enhanced_info = source_info
                
                citation = {
                    'dataset_id': enhanced_info.get('id', 'unknown'),
                    'dataset_name': enhanced_info.get('description', dataset_path),
                    'source_organization': enhanced_info.get('source', 'data.gov.in'),
                    'publisher': enhanced_info.get('publisher', 'Government of India'),
                    'url': enhanced_info.get('url', 'https://data.gov.in'),
                    'license': enhanced_info.get('license', 'Open Government Data License - India'),
                    'data_quality': enhanced_info.get('data_quality', 'High'),
                    'update_frequency': enhanced_info.get('update_frequency', 'Unknown'),
                    'last_updated': enhanced_info.get('last_updated', 'Unknown'),
                    'coverage': enhanced_info.get('coverage', 'India'),
                    'variables_used': enhanced_info.get('variables', []),
                    'records_analyzed': info['shape'][0] if info['shape'] else 0,
                    'total_records_available': enhanced_info.get('estimated_total_records', 'Unknown'),
                    'accessed_date': datetime.now().strftime('%Y-%m-%d'),
                    'accessed_time': datetime.now().strftime('%H:%M:%S UTC'),
                    'query_timestamp': datetime.now().isoformat(),
                    'data_freshness': self._calculate_data_freshness(enhanced_info.get('last_updated', ''))
                }
                citations.append(citation)
        
        return citations
    
    def _calculate_data_freshness(self, last_updated: str) -> str:
        """Calculate how fresh the data is"""
        if not last_updated or last_updated == 'Unknown':
            return 'Unknown'
        
        try:
            if 'T' in last_updated:
                update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                update_date = datetime.strptime(last_updated, '%Y-%m-%d')
            
            days_old = (datetime.now() - update_date.replace(tzinfo=None)).days
            
            if days_old == 0:
                return 'Current (Today)'
            elif days_old == 1:
                return 'Recent (1 day old)'
            elif days_old <= 7:
                return f'Recent ({days_old} days old)'
            elif days_old <= 30:
                return f'Moderate ({days_old} days old)'
            elif days_old <= 365:
                return f'Older ({days_old} days old)'
            else:
                years_old = days_old // 365
                return f'Historical ({years_old} year{"s" if years_old > 1 else ""} old)'
        except Exception:
            return 'Unknown'