"""
Data Handler Module for Project Samarth
Handles data fetching, processing, and standardization from data.gov.in APIs
Supports heterogeneous data sources: CSV, JSON, XLS
"""

import pandas as pd
import requests
import json
import os
import hashlib
import pickle
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataHandler:
    """
    Handles data operations for agricultural and meteorological datasets
    """
    
    def __init__(self, cache_dir: str = "data/cache", data_dir: str = "../data"):
        self.cache_dir = cache_dir
        # Resolve data_dir to absolute path
        if not os.path.isabs(data_dir):
            # Get the directory where this file is located (backend/utils)
            current_dir = os.path.dirname(__file__)
            # Go up two levels to get to project root, then to data
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.data_dir = os.path.join(project_root, "data")
        else:
            self.data_dir = data_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize query cache for faster repeated queries
        self.query_cache = {}
        self.query_cache_file = os.path.join(cache_dir, "query_cache.pkl")
        self.cache_timeout = 3600  # 1 hour in seconds
        self._load_query_cache()
        
        # Enhanced dataset registry with complete traceability
        self.dataset_registry = {
            'agriculture': {
                'market_prices': {
                    'id': '9ef84268-d588-465a-a308-a864a43d0070',
                    'local_file': '9ef84268-d588-465a-a308-a864a43d0070.csv',
                    'format': 'csv',
                    'description': 'Daily Agricultural Market Prices - Real-time Data from Mandis',
                    'source': 'Ministry of Agriculture & Farmers Welfare',
                    'url': 'https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070',
                    'publisher': 'Department of Agriculture and Co-operation',
                    'data_quality': 'High',
                    'update_frequency': 'Daily',
                    'last_updated': '2025-10-25',
                    'license': 'Open Government Data License - India',
                    'coverage': 'Pan-India',
                    'variables': ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade', 'Price']
                },
                'crop_production': {
                    'id': 'processed_agriculture_data',
                    'local_file': 'processed_agriculture_data.csv',
                    'format': 'csv',
                    'description': 'Processed Crop Production and Market Data by State and District',
                    'source': 'Ministry of Agriculture & Farmers Welfare',
                    'url': 'https://data.gov.in/resource/processed-agriculture-data',
                    'publisher': 'Directorate of Economics and Statistics',
                    'data_quality': 'High',
                    'update_frequency': 'Daily',
                    'last_updated': '2025-10-25',
                    'license': 'Open Government Data License - India',
                    'coverage': 'Pan-India',
                    'variables': ['State', 'District', 'Crop', 'Prices', 'Market']
                },
                'state_wise_production': {
                    'id': 'sample_agriculture_crop_production',
                    'local_file': 'sample_agriculture_crop_production.csv',
                    'format': 'csv',
                    'description': 'Historical Crop Production Statistics by State (2016-2020)',
                    'source': 'Ministry of Agriculture & Farmers Welfare',
                    'url': 'https://data.gov.in/resource/sample-crop-production',
                    'publisher': 'Directorate of Economics and Statistics',
                    'data_quality': 'High',
                    'update_frequency': 'Annual',
                    'last_updated': '2021-03-31',
                    'license': 'Open Government Data License - India',
                    'coverage': 'Pan-India',
                    'variables': ['State', 'Crop', 'Production', 'Area', 'Yield', 'Year']
                }
            },
            'meteorology': {
                'rainfall_districts': {
                    'id': 'rainfall_by_districts_2019',
                    'local_file': 'rainfall_by_districts_2019.csv',
                    'format': 'csv',
                    'description': 'District-wise Rainfall Data for Monsoon Season (2017-2018)',
                    'source': 'India Meteorological Department (IMD)',
                    'url': 'https://data.gov.in/resource/rainfall-districts-2019',
                    'publisher': 'Ministry of Earth Sciences',
                    'data_quality': 'High',
                    'update_frequency': 'Seasonal',
                    'last_updated': '2019-12-31',
                    'license': 'Open Government Data License - India',
                    'coverage': 'Pan-India',
                    'variables': ['State', 'District', 'Rainfall', 'Season', 'Year']
                },
                'rainfall_data': {
                    'id': 'sample_meteorology_rainfall_data',
                    'local_file': 'sample_meteorology_rainfall_data.csv',
                    'format': 'csv',
                    'description': 'State-wise Annual Rainfall Data with Seasonal Breakdown (2016-2020)',
                    'source': 'India Meteorological Department (IMD)',
                    'url': 'https://data.gov.in/resource/sample-rainfall-data',
                    'publisher': 'Ministry of Earth Sciences',
                    'data_quality': 'High',
                    'update_frequency': 'Annual',
                    'last_updated': '2021-02-28',
                    'license': 'Open Government Data License - India',
                    'coverage': 'Pan-India',
                    'variables': ['State', 'Annual_Rainfall', 'Monsoon_Rainfall', 'Winter_Rainfall', 'Summer_Rainfall']
                }
            }
        }
    
    def fetch_data(self, dataset_category: str, dataset_name: str, 
                   use_cache: bool = True, filters: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """
        Fetch data from local files
        
        Args:
            dataset_category: Category of dataset (agriculture/meteorology)
            dataset_name: Name of specific dataset
            use_cache: Whether to use cached data if available
            filters: Filters to apply to the data
            
        Returns:
            DataFrame containing the fetched data
        """
        try:
            # Get dataset info
            if dataset_category not in self.dataset_registry:
                logger.error(f"Unknown dataset category: {dataset_category}")
                return None
                
            if dataset_name not in self.dataset_registry[dataset_category]:
                logger.error(f"Unknown dataset: {dataset_name} in {dataset_category}")
                return None
            
            dataset_info = self.dataset_registry[dataset_category][dataset_name]
            cache_file = os.path.join(self.cache_dir, f"{dataset_category}_{dataset_name}.csv")
            
            # Check cache first
            if use_cache and os.path.exists(cache_file):
                logger.info(f"Loading cached data: {cache_file}")
                df = pd.read_csv(cache_file)
            else:
                # Load from local file
                local_file_path = os.path.join(self.data_dir, dataset_info['local_file'])
                
                if not os.path.exists(local_file_path):
                    logger.error(f"Local file not found: {local_file_path}")
                    return None
                
                logger.info(f"Loading data from local file: {local_file_path}")
                
                # Read the file based on format
                if dataset_info['format'] == 'csv':
                    df = pd.read_csv(local_file_path)
                elif dataset_info['format'] == 'json':
                    df = pd.read_json(local_file_path)
                else:
                    # Try to read as CSV by default
                    df = pd.read_csv(local_file_path)
                
                # Standardize column names
                df = self._standardize_columns(df)
                
                # Cache the processed data
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                df.to_csv(cache_file, index=False)
                logger.info(f"Data cached to: {cache_file}")
            
            # Apply filters if provided
            if filters:
                df = self._apply_local_filters(df, filters)
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names and data types based on the actual data structure
        """
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Convert column names to lowercase and replace spaces/special chars with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_').str.replace('(', '').str.replace(')', '').str.replace("'", "")
        
        # Common column mappings for different dataset types
        column_mappings = {
            # Market prices data mappings
            'state': 'state',
            'district': 'district',
            'market': 'market',
            'commodity': 'crop',
            'variety': 'variety',
            'grade': 'grade',
            'arrival_date': 'date',
            'min_x0020_price': 'min_price',
            'max_x0020_price': 'max_price',
            'modal_x0020_price': 'modal_price',
            
            # Crop production data mappings
            'crop_name': 'crop',
            'state_name': 'state',
            'district_name': 'district',
            'crop_year': 'year',
            'season_name': 'season',
            'production_in_tonnes': 'production',
            'area_in_hectares': 'area',
            'yield_kg_per_hectare': 'yield',
            
            # Rainfall data mappings
            'total_actual_rainfall_juneto_mayinmm': 'total_actual_rainfall',
            'total_normal_rainfall_juneto_mayinmm': 'total_normal_rainfall',
            'actual_rainfall_in_south_west_monsoon_juneto_septemberinmm': 'sw_monsoon_actual',
            'normal_rainfall_in_south_west_monsoon_juneto_septemberinmm': 'sw_monsoon_normal',
            'actual_rainfall_in_north_east_monsoon_octoberto_decemberinmm': 'ne_monsoon_actual',
            'normal_rainfall_in_north_east_monsoon_octoberto_decemberinmm': 'ne_monsoon_normal',
            'actual_rainfall_in_winter_season_januaryto_and_februaryinmm': 'winter_actual',
            'normal_rainfall_in_winter_season_januaryto_and_februaryinmm': 'winter_normal',
            'actual_rainfall_in_hot_weather_season_marchto_mayinmm': 'summer_actual',
            'normal_rainfall_in_hot_weather_season_marchto_mayinmm': 'summer_normal'
        }
        
        # Apply mappings
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Convert date columns if they exist
        date_columns = ['date', 'arrival_date']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                except:
                    pass
        
        # Convert numeric columns
        numeric_columns = ['production', 'area', 'yield', 'min_price', 'max_price', 'modal_price',
                          'total_actual_rainfall', 'total_normal_rainfall', 
                          'sw_monsoon_actual', 'sw_monsoon_normal',
                          'ne_monsoon_actual', 'ne_monsoon_normal',
                          'winter_actual', 'winter_normal',
                          'summer_actual', 'summer_normal']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Extract year from date if available and year column doesn't exist
        if 'date' in df.columns and 'year' not in df.columns:
            df['year'] = df['date'].dt.year
        
        # Clean state and district names
        text_columns = ['state', 'district', 'crop', 'variety']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
        
        return df
    
    def _apply_local_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the loaded dataframe
        """
        filtered_df = df.copy()
        
        for key, value in filters.items():
            if key in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df
    
    def integrate_datasets(self, datasets: List[pd.DataFrame], 
                          join_keys: List[str]) -> pd.DataFrame:
        """
        Integrate multiple datasets using common keys
        
        Args:
            datasets: List of DataFrames to integrate
            join_keys: Common columns to join on
            
        Returns:
            Integrated DataFrame
        """
        if not datasets:
            return pd.DataFrame()
        
        result = datasets[0]
        
        for df in datasets[1:]:
            result = pd.merge(result, df, on=join_keys, how='outer', suffixes=('', '_y'))
        
        return result
    
    def get_dataset_info(self, dataset_category: str, dataset_name: str) -> Dict[str, Any]:
        """
        Get metadata about a specific dataset
        """
        if (dataset_category in self.dataset_registry and 
            dataset_name in self.dataset_registry[dataset_category]):
            
            info = self.dataset_registry[dataset_category][dataset_name].copy()
            info['category'] = dataset_category
            info['name'] = dataset_name
            return info
        
        return {}
    
    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for datasets based on query terms
        """
        results = []
        query_lower = query.lower()
        
        for category, datasets in self.dataset_registry.items():
            for name, info in datasets.items():
                if (query_lower in name.lower() or 
                    query_lower in info['description'].lower() or
                    query_lower in category.lower()):
                    
                    result = info.copy()
                    result['category'] = category
                    result['name'] = name
                    results.append(result)
        
        return results
    
    def _load_query_cache(self):
        """Load query cache from disk"""
        try:
            if os.path.exists(self.query_cache_file):
                with open(self.query_cache_file, 'rb') as f:
                    self.query_cache = pickle.load(f)
                logger.info(f"Loaded query cache with {len(self.query_cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to load query cache: {e}")
            self.query_cache = {}
    
    def _save_query_cache(self):
        """Save query cache to disk"""
        try:
            with open(self.query_cache_file, 'wb') as f:
                pickle.dump(self.query_cache, f)
            logger.info(f"Saved query cache with {len(self.query_cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to save query cache: {e}")
    
    def _get_query_hash(self, query_params: Dict[str, Any]) -> str:
        """Generate hash for query parameters"""
        query_str = json.dumps(query_params, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def get_cached_query_result(self, query_params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result for query parameters"""
        query_hash = self._get_query_hash(query_params)
        
        if query_hash in self.query_cache:
            cache_entry = self.query_cache[query_hash]
            cache_time = cache_entry.get('timestamp', 0)
            
            # Check if cache is still valid
            if datetime.now().timestamp() - cache_time < self.cache_timeout:
                logger.info(f"Using cached result for query hash: {query_hash[:8]}...")
                return cache_entry.get('result')
            else:
                # Remove expired cache entry
                del self.query_cache[query_hash]
        
        return None
    
    def cache_query_result(self, query_params: Dict[str, Any], result: Any):
        """Cache query result"""
        query_hash = self._get_query_hash(query_params)
        
        self.query_cache[query_hash] = {
            'timestamp': datetime.now().timestamp(),
            'result': result,
            'query_params': query_params
        }
        
        # Clean up old cache entries (keep only last 100)
        if len(self.query_cache) > 100:
            oldest_entries = sorted(
                self.query_cache.items(),
                key=lambda x: x[1]['timestamp']
            )[:len(self.query_cache) - 100]
            
            for entry_hash, _ in oldest_entries:
                del self.query_cache[entry_hash]
        
        self._save_query_cache()
        logger.info(f"Cached result for query hash: {query_hash[:8]}...")
    
    def get_enhanced_dataset_info(self, dataset_category: str, dataset_name: str) -> Dict[str, Any]:
        """Get enhanced dataset information with full traceability"""
        if (dataset_category in self.dataset_registry and 
            dataset_name in self.dataset_registry[dataset_category]):
            
            info = self.dataset_registry[dataset_category][dataset_name].copy()
            info['category'] = dataset_category
            info['name'] = dataset_name
            
            # Add file statistics if available
            local_file_path = os.path.join(self.data_dir, info['local_file'])
            if os.path.exists(local_file_path):
                stat = os.stat(local_file_path)
                info['file_size'] = stat.st_size
                info['file_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Get basic data statistics
                try:
                    df = pd.read_csv(local_file_path, nrows=1000)  # Sample for stats
                    info['columns'] = df.columns.tolist()
                    info['sample_records'] = len(df)
                    info['estimated_total_records'] = int(stat.st_size / (stat.st_size / len(df))) if len(df) > 0 else 0
                except Exception as e:
                    logger.warning(f"Could not get data statistics: {e}")
            
            return info
        
        return {}

class DataProcessor:
    """
    Process and clean agricultural and meteorological data
    """
    
    @staticmethod
    def clean_agricultural_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean agricultural production data
        """
        if df.empty:
            return df
        
        # Remove rows with missing critical data
        critical_columns = ['state', 'crop', 'year']
        for col in critical_columns:
            if col in df.columns:
                df = df.dropna(subset=[col])
        
        # Convert numeric columns
        numeric_columns = ['production', 'area', 'yield', 'year']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with zero or negative production
        if 'production' in df.columns:
            df = df[df['production'] > 0]
        
        # Standardize state names
        if 'state' in df.columns:
            df['state'] = df['state'].str.title().str.strip()
        
        # Standardize crop names
        if 'crop' in df.columns:
            df['crop'] = df['crop'].str.title().str.strip()
        
        return df
    
    @staticmethod
    def clean_rainfall_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean rainfall data
        """
        if df.empty:
            return df
        
        # Convert rainfall to numeric
        if 'rainfall' in df.columns:
            df['rainfall'] = pd.to_numeric(df['rainfall'], errors='coerce')
            # Remove negative rainfall values
            df = df[df['rainfall'] >= 0]
        
        # Convert year to numeric
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        # Standardize state names
        if 'state' in df.columns:
            df['state'] = df['state'].str.title().str.strip()
        
        return df
    
    @staticmethod
    def aggregate_by_state_year(df: pd.DataFrame, 
                               value_column: str,
                               agg_function: str = 'sum') -> pd.DataFrame:
        """
        Aggregate data by state and year
        """
        if df.empty or value_column not in df.columns:
            return pd.DataFrame()
        
        group_columns = ['state', 'year']
        existing_columns = [col for col in group_columns if col in df.columns]
        
        if not existing_columns:
            return df
        
        agg_dict = {value_column: agg_function}
        result = df.groupby(existing_columns).agg(agg_dict).reset_index()
        
        return result