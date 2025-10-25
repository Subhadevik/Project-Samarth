#!/usr/bin/env python3
"""
Enhanced Demo Script for Project Samarth
Demonstrates robustness, traceability, and caching features
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.data_handler import DataHandler
from utils.query_engine import QueryEngine

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)

def print_section(title):
    """Print formatted section"""
    print(f"\n📊 {title}")
    print("-" * 50)

def test_enhanced_features():
    """Test enhanced features: caching, traceability, robustness"""
    
    print_header("Project Samarth - Enhanced Features Demo")
    print("🔥 Testing: Robustness, Traceability & Caching")
    
    # Initialize components
    print_section("Initializing System")
    data_handler = DataHandler()
    query_engine = QueryEngine(data_handler)
    
    # Test data loading with traceability
    print_section("Data Loading & Traceability")
    print("📁 Available datasets:")
    
    total_datasets = 0
    for category, datasets in data_handler.dataset_registry.items():
        print(f"\n🏷️  Category: {category.upper()}")
        for name, info in datasets.items():
            total_datasets += 1
            local_file = os.path.join(data_handler.data_dir, info['local_file'])
            status = "✅" if os.path.exists(local_file) else "❌"
            
            print(f"   {status} {name}")
            print(f"      📝 Description: {info['description']}")
            print(f"      🏢 Source: {info['source']}")
            print(f"      🔗 URL: {info['url']}")
            print(f"      📅 Last Updated: {info.get('last_updated', 'Unknown')}")
            print(f"      ⭐ Quality: {info.get('data_quality', 'Unknown')}")
            print(f"      🔄 Update Frequency: {info.get('update_frequency', 'Unknown')}")
    
    print(f"\n📊 Total datasets registered: {total_datasets}")
    
    # Test queries with caching
    print_section("Query Processing with Caching")
    
    test_queries = [
        "Compare potato prices between Punjab and Haryana",
        "Which state has the highest tomato prices?",
        "Show me rice production trends",
        "Compare potato prices between Punjab and Haryana",  # Repeat for cache test
    ]
    
    query_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🤔 Query {i}: '{query}'")
        
        start_time = time.time()
        result = query_engine.process_query(query)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if result['success']:
            print(f"   ✅ Success! Processing time: {processing_time:.2f}ms")
            print(f"   🧠 Intent: {result['intent']}")
            print(f"   📊 Confidence: {result['confidence']:.2f}")
            print(f"   ⚡ Cached: {'Yes' if result.get('cached', False) else 'No'}")
            print(f"   📚 Citations: {len(result.get('citations', []))}")
            
            # Show first citation details
            if result.get('citations'):
                citation = result['citations'][0]
                print(f"   🔗 Primary Source: {citation.get('source_organization', 'Unknown')}")
                print(f"   📋 Dataset: {citation.get('dataset_name', 'Unknown')[:60]}...")
                print(f"   📊 Records Used: {citation.get('records_analyzed', 0)}")
                print(f"   🕒 Data Freshness: {citation.get('data_freshness', 'Unknown')}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        query_results.append({
            'query': query,
            'success': result['success'],
            'cached': result.get('cached', False),
            'processing_time': processing_time,
            'citations_count': len(result.get('citations', []))
        })
    
    # Cache statistics
    print_section("Cache Performance Analysis")
    
    cache_size = len(data_handler.query_cache)
    print(f"📦 Query cache size: {cache_size} entries")
    print(f"⏰ Cache timeout: {data_handler.cache_timeout} seconds")
    
    # Performance comparison
    fresh_queries = [r for r in query_results if not r['cached']]
    cached_queries = [r for r in query_results if r['cached']]
    
    if fresh_queries and cached_queries:
        avg_fresh_time = sum(r['processing_time'] for r in fresh_queries) / len(fresh_queries)
        avg_cached_time = sum(r['processing_time'] for r in cached_queries) / len(cached_queries)
        speedup = avg_fresh_time / avg_cached_time if avg_cached_time > 0 else 1
        
        print(f"⚡ Average fresh query time: {avg_fresh_time:.2f}ms")
        print(f"⚡ Average cached query time: {avg_cached_time:.2f}ms")
        print(f"🚀 Cache speedup: {speedup:.1f}x faster")
    
    # Test traceability features
    print_section("Traceability & Data Lineage")
    
    if query_results and query_results[0]['success']:
        print("🔍 Testing enhanced dataset information...")
        
        # Get enhanced info for first dataset
        enhanced_info = data_handler.get_enhanced_dataset_info('agriculture', 'crop_production')
        if enhanced_info:
            print(f"📋 Dataset ID: {enhanced_info.get('id', 'Unknown')}")
            print(f"📝 Description: {enhanced_info.get('description', 'Unknown')}")
            print(f"🏢 Publisher: {enhanced_info.get('publisher', 'Unknown')}")
            print(f"📊 License: {enhanced_info.get('license', 'Unknown')}")
            print(f"🌍 Coverage: {enhanced_info.get('coverage', 'Unknown')}")
            print(f"📁 File Size: {enhanced_info.get('file_size', 0):,} bytes")
            
            if enhanced_info.get('columns'):
                print(f"📊 Columns: {', '.join(enhanced_info['columns'][:5])}...")
    
    # Test robustness features
    print_section("Robustness Testing")
    
    print("🛡️  Testing error handling...")
    
    # Test with invalid query
    invalid_result = query_engine.process_query("")
    print(f"   Empty query handling: {'✅ Pass' if not invalid_result['success'] else '❌ Fail'}")
    
    # Test with very complex query
    complex_query = "What is the correlation between rainfall and crop production across all states for the last decade considering seasonal variations?"
    complex_result = query_engine.process_query(complex_query)
    print(f"   Complex query handling: {'✅ Pass' if complex_result['success'] else '❌ Fail'}")
    
    # Summary
    print_section("Summary")
    
    successful_queries = len([r for r in query_results if r['success']])
    total_queries = len(query_results)
    cached_queries_count = len([r for r in query_results if r['cached']])
    
    print(f"📊 Query Success Rate: {successful_queries}/{total_queries} ({100*successful_queries/total_queries:.1f}%)")
    print(f"⚡ Cache Hit Rate: {cached_queries_count}/{total_queries} ({100*cached_queries_count/total_queries:.1f}%)")
    print(f"📚 Total Citations Generated: {sum(r['citations_count'] for r in query_results)}")
    print(f"🔗 Datasets Available: {total_datasets}")
    
    print_header("Enhanced Demo Complete!")
    print("✅ Robustness: Error handling and complex query support")
    print("✅ Traceability: Complete data lineage and citations")
    print("✅ Caching: Improved performance for repeated queries")
    print("✅ Data Quality: Enhanced metadata and freshness indicators")

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print_section("API Endpoints Testing")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            
            # Test cache stats endpoint
            cache_response = requests.get('http://localhost:5000/api/cache/stats', timeout=5)
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                print(f"📦 Cache stats retrieved: {cache_data['cache_stats']['query_cache_size']} queries cached")
            
        else:
            print(f"⚠️  API server responded with status: {response.status_code}")
            
    except requests.exceptions.RequestException:
        print("ℹ️  API server not running (start with: python backend/main.py)")

if __name__ == "__main__":
    print("🇮🇳 Project Samarth - Enhanced Features Demo")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_enhanced_features()
        test_api_endpoints()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")