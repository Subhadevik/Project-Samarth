#!/usr/bin/env python3
"""
Project Samarth - Setup and Demonstration Script
Prepares the system to work with local datasets without API keys
"""

import os
import sys
import pandas as pd
from pathlib import Path

def setup_environment():
    """Set up the environment and verify data files"""
    print("🌾 Setting up Project Samarth...")
    
    # Get project root directory
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    cache_dir = data_dir / "cache"
    
    # Create necessary directories
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Project root: {project_root}")
    print(f"📊 Data directory: {data_dir}")
    
    # Check for required data files
    required_files = [
        "9ef84268-d588-465a-a308-a864a43d0070.csv",
        "rainfall_by_districts_2019.csv",
        "sample_agriculture_crop_production.csv",
        "sample_meteorology_rainfall_data.csv",
        "processed_agriculture_data.csv"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} required files are missing.")
        print("The system will work with available data files.")
    else:
        print("\n✅ All required data files are present!")
    
    return project_root, len(missing_files) == 0

def test_data_loading():
    """Test loading and processing of data files"""
    print("\n🔄 Testing data loading...")
    
    sys.path.append(str(Path(__file__).parent / "backend"))
    
    try:
        from utils.data_handler import DataHandler
        
        # Initialize data handler
        data_handler = DataHandler(
            cache_dir="../data/cache",
            data_dir="../data"
        )
        
        # Test loading different datasets
        test_datasets = [
            ("agriculture", "crop_production"),
            ("agriculture", "market_prices"),
            ("meteorology", "rainfall_districts"),
            ("meteorology", "rainfall_data")
        ]
        
        loaded_datasets = 0
        for category, name in test_datasets:
            try:
                df = data_handler.fetch_data(category, name)
                if df is not None and not df.empty:
                    print(f"✅ Loaded {category}.{name}: {df.shape[0]} records, {df.shape[1]} columns")
                    print(f"   Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                    loaded_datasets += 1
                else:
                    print(f"❌ Failed to load {category}.{name}")
            except Exception as e:
                print(f"❌ Error loading {category}.{name}: {str(e)}")
        
        print(f"\n📊 Successfully loaded {loaded_datasets}/{len(test_datasets)} datasets")
        return loaded_datasets > 0
        
    except Exception as e:
        print(f"❌ Error initializing data handler: {str(e)}")
        return False

def demonstrate_queries():
    """Demonstrate example queries"""
    print("\n🤖 Testing query processing...")
    
    try:
        sys.path.append(str(Path(__file__).parent / "backend"))
        
        from utils.data_handler import DataHandler
        from utils.query_engine import QueryEngine
        
        # Initialize components
        data_handler = DataHandler(cache_dir="../data/cache", data_dir="../data")
        query_engine = QueryEngine(data_handler)
        
        # Test queries
        test_queries = [
            "Which state has the highest rice production?",
            "Compare cotton production between Gujarat and Rajasthan",
            "Show me the rainfall data for Tamil Nadu districts"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test Query {i}: {query}")
            
            try:
                response = query_engine.process_query(query)
                if response.get('success'):
                    print(f"✅ Query processed successfully")
                    print(f"   Intent: {response.get('intent', 'Unknown')}")
                    print(f"   Confidence: {response.get('confidence', 0):.2f}")
                    print(f"   Answer: {response.get('answer', 'No answer')[:100]}...")
                else:
                    print(f"❌ Query failed: {response.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Query error: {str(e)}")
        
        print("\n✅ Query processing test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in query demonstration: {str(e)}")
        return False

def show_sample_data():
    """Show sample data from each dataset"""
    print("\n📋 Sample Data Preview:")
    
    try:
        data_dir = Path(__file__).parent / "data"
        
        # Show samples from each file
        files_to_show = [
            ("🌾 Market Prices", "9ef84268-d588-465a-a308-a864a43d0070.csv"),
            ("🌧️  Rainfall by Districts", "rainfall_by_districts_2019.csv"),
            ("📊 Crop Production", "processed_agriculture_data.csv")
        ]
        
        for title, filename in files_to_show:
            file_path = data_dir / filename
            if file_path.exists():
                print(f"\n{title} ({filename}):")
                df = pd.read_csv(file_path)
                print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"   Columns: {', '.join(df.columns[:4])}{'...' if len(df.columns) > 4 else ''}")
                print("   Sample records:")
                for _, row in df.head(2).iterrows():
                    row_str = ', '.join([f"{col}: {val}" for col, val in row.items()[:3]])
                    print(f"     {row_str}...")
            else:
                print(f"\n{title}: File not found")
                
    except Exception as e:
        print(f"❌ Error showing sample data: {str(e)}")

def main():
    """Main setup and demonstration function"""
    print("=" * 60)
    print("🇮🇳 Project Samarth - Agricultural Intelligence System")
    print("   Working with Local Datasets (No API Key Required)")
    print("=" * 60)
    
    # Setup environment
    project_root, all_files_present = setup_environment()
    
    # Show sample data
    show_sample_data()
    
    # Test data loading
    data_loading_ok = test_data_loading()
    
    # Demonstrate queries
    if data_loading_ok:
        query_demo_ok = demonstrate_queries()
    else:
        print("⚠️  Skipping query demonstration due to data loading issues")
        query_demo_ok = False
    
    # Final status
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY:")
    print(f"   ✅ Environment setup: {'✓' if True else '✗'}")
    print(f"   ✅ All data files present: {'✓' if all_files_present else '✗'}")
    print(f"   ✅ Data loading: {'✓' if data_loading_ok else '✗'}")
    print(f"   ✅ Query processing: {'✓' if query_demo_ok else '✗'}")
    
    if data_loading_ok:
        print("\n🚀 System is ready! To start the web interface:")
        print("   cd backend")
        print("   python main.py")
        print("\n   Then open: http://localhost:5000")
        
        print("\n💡 Try asking questions like:")
        print("   • 'Which state has the highest cotton production?'")
        print("   • 'Compare rainfall between Chennai and Salem districts'")
        print("   • 'Show me banana production across different states'")
    else:
        print("\n⚠️  Please check data files and try again.")
    
    print("\n🌾 Project Samarth setup complete!")

if __name__ == "__main__":
    main()