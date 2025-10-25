"""
Simple Query Engine for Project Samarth
Works without pandas and advanced NLP
"""

import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleQueryEngine:
    """Simple query engine that works without pandas"""
    
    def __init__(self, data_handler):
        self.data_handler = data_handler
        
    def process_query(self, query):
        """Process a simple query and return response"""
        
        # Generate query hash for caching
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        
        # Check cache first
        cached_result = self.data_handler.get_cached_result(query_hash)
        if cached_result:
            cached_result['from_cache'] = True
            return cached_result
        
        # Simple keyword-based query processing
        query_lower = query.lower()
        
        # Determine query type and fetch relevant data
        data = []
        response_text = ""
        
        if any(word in query_lower for word in ['rice', 'wheat', 'crop', 'production']):
            data = self.data_handler.fetch_data('agriculture', 'crop_production')
            response_text = self._generate_agriculture_response(query_lower, data)
        elif any(word in query_lower for word in ['rain', 'rainfall', 'weather', 'climate']):
            data = self.data_handler.fetch_data('meteorology', 'rainfall_data')
            response_text = self._generate_meteorology_response(query_lower, data)
        else:
            # General response
            data = self.data_handler.fetch_data('agriculture', 'crop_production')
            response_text = "I can help you with information about Indian agriculture and climate data. Try asking about crop production, rainfall, or specific states."
        
        # Create response
        response = {
            'success': True,
            'answer': response_text,
            'data': data[:10],  # Limit to 10 records
            'query_type': 'simple',
            'confidence': 0.7,
            'citations': self._get_citations(),
            'from_cache': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the result
        self.data_handler.cache_query_result(query_hash, response)
        
        return response
    
    def _generate_agriculture_response(self, query, data):
        """Generate response for agriculture queries"""
        
        if 'compare' in query:
            if len(data) >= 2:
                return f"Based on the agricultural data, I can see production statistics for multiple states and crops. For example, {data[0]['State']} produced {data[0]['Production']} units of {data[0]['Crop']} in {data[0]['Year']}, while {data[1]['State']} produced {data[1]['Production']} units."
        
        if 'punjab' in query:
            punjab_data = [d for d in data if d.get('State', '').lower() == 'punjab']
            if punjab_data:
                return f"Punjab's agricultural data shows production of {punjab_data[0]['Production']} units of {punjab_data[0]['Crop']} in {punjab_data[0]['Year']}."
        
        if 'highest' in query or 'maximum' in query:
            if data:
                max_prod = max(data, key=lambda x: x.get('Production', 0))
                return f"The highest production recorded is {max_prod['Production']} units of {max_prod['Crop']} in {max_prod['State']} during {max_prod['Year']}."
        
        # Default agriculture response
        return f"I found {len(data)} agricultural records. The data includes crop production statistics from various Indian states including rice, wheat, and other major crops."
    
    def _generate_meteorology_response(self, query, data):
        """Generate response for meteorology queries"""
        
        if 'maharashtra' in query:
            mh_data = [d for d in data if d.get('State', '').lower() == 'maharashtra']
            if mh_data:
                return f"Maharashtra received {mh_data[0]['Rainfall']} mm of rainfall in {mh_data[0]['Month']} {mh_data[0]['Year']}."
        
        if 'highest' in query or 'maximum' in query:
            if data:
                max_rain = max(data, key=lambda x: x.get('Rainfall', 0))
                return f"The highest rainfall recorded is {max_rain['Rainfall']} mm in {max_rain['State']} during {max_rain['Month']} {max_rain['Year']}."
        
        # Default meteorology response
        return f"I found rainfall data for {len(data)} locations. The data shows precipitation patterns across different Indian states."
    
    def _get_citations(self):
        """Get data source citations"""
        return [
            {
                'dataset': 'Government Agricultural Statistics',
                'description': 'Official crop production data from Ministry of Agriculture & Farmers Welfare',
                'url': 'https://data.gov.in/resource/crop-production-statistics',
                'last_updated': '2023-01-01',
                'data_quality': 'Verified'
            },
            {
                'dataset': 'India Meteorological Department',
                'description': 'Rainfall and weather data from IMD',
                'url': 'https://data.gov.in/resource/rainfall-statistics',
                'last_updated': '2023-01-01',
                'data_quality': 'High'
            }
        ]