# Backend utilities __init__.py
# Import handlers based on availability

try:
    import pandas as pd
    # If pandas is available, import full features
    from .data_handler import DataHandler, DataProcessor
    from .nlp_processor import NLPProcessor, QueryMapper, QueryAnalysis, QueryType
    from .query_engine import QueryEngine
    PANDAS_AVAILABLE = True
except ImportError:
    # If pandas is not available, use simple handlers
    from .simple_data_handler import SimpleDataHandler as DataHandler
    from .simple_query_engine import SimpleQueryEngine as QueryEngine
    PANDAS_AVAILABLE = False
    
    # Dummy classes for compatibility
    class DataProcessor:
        pass
    class NLPProcessor:
        pass
    class QueryMapper:
        pass
    class QueryAnalysis:
        pass
    class QueryType:
        pass

__all__ = [
    'DataHandler',
    'DataProcessor', 
    'NLPProcessor',
    'QueryMapper',
    'QueryAnalysis',
    'QueryType',
    'QueryEngine',
    'PANDAS_AVAILABLE'
]