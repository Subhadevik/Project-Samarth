"""
Fallback Data Handler for Project Samarth
Works without pandas for basic deployment
"""

import json
import os
from datetime import datetime
import hashlib
import logging
import pickle

logger = logging.getLogger(__name__)

class SimpleDataHandler:
    """Simple data handler that works without pandas"""
    
    def __init__(self, cache_dir='../data/cache', data_dir='../data'):
        self.cache_dir = cache_dir
        self.data_dir = data_dir
        self.query_cache = {}
        self.cache_timeout = 3600  # 1 hour
        
        # Create directories
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Simple dataset registry
        self.dataset_registry = {
            'agriculture': {
                'crop_production': {
                    'description': 'Agricultural crop production data from data.gov.in',
                    'url': 'https://data.gov.in/resource/crop-production-statistics',
                    'last_updated': '2023-01-01',
                    'data_quality': 'Verified'
                }
            },
            'meteorology': {
                'rainfall_data': {
                    'description': 'Rainfall data from India Meteorological Department',
                    'url': 'https://data.gov.in/resource/rainfall-statistics',
                    'last_updated': '2023-01-01',
                    'data_quality': 'High'
                }
            }
        }
        
        # Load cache
        self._load_query_cache()
    
    def _load_query_cache(self):
        """Load query cache from disk"""
        cache_file = os.path.join(self.cache_dir, 'query_cache.pkl')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    self.query_cache = pickle.load(f)
                logger.info(f"Loaded query cache with {len(self.query_cache)} entries")
        except Exception as e:
            logger.warning(f"Could not load query cache: {e}")
            self.query_cache = {}
    
    def _save_query_cache(self):
        """Save query cache to disk"""
        cache_file = os.path.join(self.cache_dir, 'query_cache.pkl')
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.query_cache, f)
        except Exception as e:
            logger.warning(f"Could not save query cache: {e}")
    
    def fetch_data(self, category, name, use_cache=True):
        """Fetch sample data - returns simple dictionary structure"""
        
        # Return sample data for demo purposes
        if category == 'agriculture' and name == 'crop_production':
            return [
                {'State': 'Punjab', 'Crop': 'Rice', 'Production': 11000, 'Year': 2020},
                {'State': 'Haryana', 'Crop': 'Rice', 'Production': 8500, 'Year': 2020},
                {'State': 'Punjab', 'Crop': 'Wheat', 'Production': 15000, 'Year': 2020},
                {'State': 'Haryana', 'Crop': 'Wheat', 'Production': 12000, 'Year': 2020},
                {'State': 'Uttar Pradesh', 'Crop': 'Rice', 'Production': 14000, 'Year': 2020},
                {'State': 'Uttar Pradesh', 'Crop': 'Wheat', 'Production': 18000, 'Year': 2020}
            ]
        elif category == 'meteorology' and name == 'rainfall_data':
            return [
                {'State': 'Punjab', 'Rainfall': 650, 'Year': 2020, 'Month': 'July'},
                {'State': 'Haryana', 'Rainfall': 580, 'Year': 2020, 'Month': 'July'},
                {'State': 'Maharashtra', 'Rainfall': 1200, 'Year': 2020, 'Month': 'July'},
                {'State': 'West Bengal', 'Rainfall': 1100, 'Year': 2020, 'Month': 'July'}
            ]
        
        return []
    
    def get_dataset_info(self, category, name):
        """Get information about a dataset"""
        if category in self.dataset_registry and name in self.dataset_registry[category]:
            return self.dataset_registry[category][name]
        return None
    
    def search_datasets(self, query):
        """Search for datasets based on query"""
        results = []
        query_lower = query.lower()
        
        for category, datasets in self.dataset_registry.items():
            for name, info in datasets.items():
                if (query_lower in info['description'].lower() or 
                    query_lower in name.lower()):
                    results.append({
                        'category': category,
                        'name': name,
                        'description': info['description'],
                        'url': info['url']
                    })
        
        return results
    
    def cache_query_result(self, query_hash, result):
        """Cache a query result"""
        self.query_cache[query_hash] = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'ttl': self.cache_timeout
        }
        self._save_query_cache()
    
    def get_cached_result(self, query_hash):
        """Get a cached query result if valid"""
        if query_hash in self.query_cache:
            cached = self.query_cache[query_hash]
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if (datetime.now() - cached_time).seconds < cached['ttl']:
                return cached['result']
        return None