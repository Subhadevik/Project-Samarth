"""
API Routes Module for Project Samarth
Modular route definitions for better organization
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from ..utils.query_engine import QueryEngine

logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_routes(query_engine: QueryEngine):
    """Initialize routes with query engine instance"""
    
    @api_bp.route('/v1/query', methods=['POST'])
    def process_query_v1():
        """
        Enhanced query processing endpoint with additional features
        """
        try:
            data = request.get_json()
            query = data.get('query', '').strip()
            options = data.get('options', {})
            
            if not query:
                return jsonify({
                    'success': False,
                    'error': 'Query is required'
                }), 400
            
            # Process with options
            response = query_engine.process_query(query)
            
            # Apply options
            if options.get('include_raw_data', False):
                response['raw_data'] = response.get('data', {})
            
            if options.get('detailed_citations', True):
                # Enhanced citations are already included
                pass
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in v1 query processing: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return api_bp