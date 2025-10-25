"""
Main Flask Application for Project Samarth
Intelligent Q&A system for India's agricultural economy and climate patterns
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
from datetime import datetime
import traceback

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our custom modules
try:
    from utils.data_handler import DataHandler
    from utils.query_engine import QueryEngine
    FULL_FEATURES = True
    logger.info("Full features loaded successfully")
except ImportError as e:
    logger.warning(f"Full features not available: {e}")
    try:
        from utils.simple_data_handler import SimpleDataHandler as DataHandler
        from utils.simple_query_engine import SimpleQueryEngine as QueryEngine
        FULL_FEATURES = False
        logger.info("Using simplified features for deployment")
    except ImportError as e2:
        logger.error(f"Could not load any data handler: {e2}")
        # Create a minimal fallback
        class MinimalDataHandler:
            def __init__(self, *args, **kwargs):
                pass
        class MinimalQueryEngine:
            def __init__(self, *args, **kwargs):
                pass
            def process_query(self, query):
                return {
                    'success': True,
                    'answer': 'System is starting up. Agricultural data processing will be available shortly.',
                    'data': [],
                    'citations': []
                }
        DataHandler = MinimalDataHandler
        QueryEngine = MinimalQueryEngine
        FULL_FEATURES = False

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../frontend',
           static_folder='../frontend/static')

# Enable CORS for all routes
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'samarth-secret-key-change-in-production'
app.config['DEBUG'] = True

# Initialize components
data_handler = DataHandler(cache_dir='../data/cache', data_dir='../data')
query_engine = QueryEngine(data_handler)

@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Project Samarth API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """
    Main endpoint to process natural language queries
    
    Expected JSON payload:
    {
        "query": "Natural language question about agriculture/climate"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON',
                'answer': 'Please send your query as JSON data.'
            }), 400
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required',
                'answer': 'Please provide a query to process.'
            }), 400
        
        # Log the query
        logger.info(f"Processing query: {query}")
        
        # Process the query
        response = query_engine.process_query(query)
        
        # Add request metadata
        response['request_info'] = {
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'ip_address': request.remote_addr
        }
        
        logger.info(f"Query processed successfully. Confidence: {response.get('confidence', 0)}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'answer': 'I apologize, but I encountered an error while processing your query. Please try again later.',
            'data': {},
            'citations': []
        }), 500

@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """
    List available datasets
    """
    try:
        datasets = []
        
        # Get agriculture datasets
        for name, info in data_handler.dataset_registry['agriculture'].items():
            dataset_info = info.copy()
            dataset_info['category'] = 'agriculture'
            dataset_info['name'] = name
            datasets.append(dataset_info)
        
        # Get meteorology datasets
        for name, info in data_handler.dataset_registry['meteorology'].items():
            dataset_info = info.copy()
            dataset_info['category'] = 'meteorology'
            dataset_info['name'] = name
            datasets.append(dataset_info)
        
        return jsonify({
            'success': True,
            'datasets': datasets,
            'total': len(datasets)
        })
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'datasets': []
        }), 500

@app.route('/api/datasets/<category>/<name>', methods=['GET'])
def get_dataset_info(category, name):
    """
    Get detailed information about a specific dataset
    """
    try:
        info = data_handler.get_dataset_info(category, name)
        
        if not info:
            return jsonify({
                'success': False,
                'error': 'Dataset not found'
            }), 404
        
        # Try to get sample data
        sample_data = data_handler.fetch_data(category, name, use_cache=True)
        
        if sample_data is not None and not sample_data.empty:
            info['sample_data'] = {
                'columns': sample_data.columns.tolist(),
                'shape': sample_data.shape,
                'head': sample_data.head().to_dict('records')
            }
        
        return jsonify({
            'success': True,
            'dataset_info': info
        })
        
    except Exception as e:
        logger.error(f"Error getting dataset info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_datasets():
    """
    Search for datasets based on query terms
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required',
                'results': []
            }), 400
        
        results = data_handler.search_datasets(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching datasets: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'results': []
        }), 500

@app.route('/api/examples', methods=['GET'])
def get_example_queries():
    """
    Get example queries that users can ask
    """
    examples = [
        {
            'category': 'Comparison',
            'query': 'Compare the average annual rainfall in Punjab and Haryana for the last 5 years.',
            'description': 'Compares rainfall data between two states over a time period'
        },
        {
            'category': 'Ranking',
            'query': 'Which district has the highest rice production in India?',
            'description': 'Identifies the top-performing district for a specific crop'
        },
        {
            'category': 'Trend Analysis',
            'query': 'Analyze the wheat production trend in Uttar Pradesh over the last decade.',
            'description': 'Shows production trends over time for a specific crop and state'
        },
        {
            'category': 'Correlation',
            'query': 'How does rainfall correlate with rice production in West Bengal?',
            'description': 'Analyzes the relationship between weather and agricultural output'
        },
        {
            'category': 'General Information',
            'query': 'What is the total sugarcane production in Maharashtra in 2020?',
            'description': 'Provides specific data points for crops, states, and years'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples,
        'total': len(examples)
    })

@app.route('/api/states', methods=['GET'])
def get_indian_states():
    """
    Get list of Indian states and union territories
    """
    states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
        'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
        'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh',
        'West Bengal', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Chandigarh',
        'Dadra and Nagar Haveli', 'Daman and Diu', 'Lakshadweep', 'Puducherry',
        'Andaman and Nicobar Islands'
    ]
    
    return jsonify({
        'success': True,
        'states': sorted(states),
        'total': len(states)
    })

@app.route('/api/crops', methods=['GET'])
def get_indian_crops():
    """
    Get list of major Indian crops
    """
    crops = [
        'Rice', 'Wheat', 'Maize', 'Barley', 'Bajra', 'Jowar', 'Ragi',
        'Sugarcane', 'Cotton', 'Jute', 'Tea', 'Coffee', 'Coconut',
        'Groundnut', 'Sesame', 'Rape', 'Mustard', 'Linseed', 'Castor',
        'Sunflower', 'Safflower', 'Niger', 'Soybean', 'Sesamum',
        'Arhar', 'Moong', 'Urad', 'Masoor', 'Gram', 'Khesari',
        'Onion', 'Potato', 'Sweet Potato', 'Tapioca', 'Banana',
        'Mango', 'Citrus', 'Apple', 'Grapes', 'Pomegranate',
        'Cashew', 'Cardamom', 'Black Pepper', 'Turmeric', 'Ginger',
        'Coriander', 'Cumin', 'Fennel', 'Fenugreek'
    ]
    
    return jsonify({
        'success': True,
        'crops': sorted(crops),
        'total': len(crops)
    })

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics for monitoring
    """
    try:
        cache_stats = {
            'query_cache_size': len(data_handler.query_cache),
            'cache_timeout': data_handler.cache_timeout,
            'cache_file_exists': os.path.exists(data_handler.query_cache_file),
            'total_datasets': sum(len(datasets) for datasets in data_handler.dataset_registry.values()),
            'available_datasets': []
        }
        
        # Get dataset availability
        for category, datasets in data_handler.dataset_registry.items():
            for name, info in datasets.items():
                local_file = os.path.join(data_handler.data_dir, info['local_file'])
                cache_stats['available_datasets'].append({
                    'category': category,
                    'name': name,
                    'description': info['description'],
                    'file_exists': os.path.exists(local_file),
                    'last_updated': info.get('last_updated', 'Unknown'),
                    'data_quality': info.get('data_quality', 'Unknown')
                })
        
        return jsonify({
            'success': True,
            'cache_stats': cache_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear query cache
    """
    try:
        old_size = len(data_handler.query_cache)
        data_handler.query_cache.clear()
        data_handler._save_query_cache()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {old_size} cached queries',
            'old_cache_size': old_size,
            'new_cache_size': 0
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist.'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint.'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Project Samarth API server...")
    
    # Create necessary directories
    os.makedirs('../data/cache', exist_ok=True)
    os.makedirs('../frontend/static', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Configure production logging
    if not app.debug:
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/samarth.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Project Samarth startup')
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )