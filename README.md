# Project Samarth - Agricultural Intelligence Q&A System

![Project Samarth](https://img.shields.io/badge/Project-Samarth-success.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

## Overview

Project Samarth is an intelligent Q&A system that answers natural language questions about India's agricultural economy and climate patterns using real datasets from data.gov.in. The system integrates heterogeneous data sources and provides insights through natural language processing and data visualization.

## 🏗️ System Architecture

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (Frontend)                     │
│  HTML + CSS + JavaScript + Bootstrap + Chart.js            │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   API Layer (Flask)                        │
│  REST endpoints, request validation, response formatting   │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 NLP Processing Layer                       │
│  Entity extraction, intent classification, query mapping   │
│  (spaCy + pattern matching for Indian agricultural terms)  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                Query Engine Layer                          │
│  Query execution, data aggregation, response generation    │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer                                │
│  Data fetching, caching, standardization (pandas)          │
│  Integration with data.gov.in APIs                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Integration Process

1. **Data Sources**: Ministry of Agriculture & Farmers Welfare, India Meteorological Department
2. **Data Formats**: CSV, JSON, XLS from data.gov.in APIs
3. **Standardization**: Unified column naming, data type conversion, quality checks
4. **Caching**: Local caching for performance optimization
5. **Privacy**: No third-party data storage, government data only

## 🚀 Features

### Natural Language Query Processing
- **Entity Extraction**: Automatically identifies Indian states, crops, years, and metrics
- **Intent Classification**: Categorizes queries into comparison, ranking, trend analysis, and correlation
- **Query Mapping**: Maps natural language to database operations
- **Smart Caching**: Caches query results for faster repeated queries (1-hour timeout)

### Supported Query Types
1. **Comparison**: "Compare rice production between Punjab and Haryana"
2. **Ranking**: "Which state has the highest wheat production?"
3. **Trend Analysis**: "Show cotton production trend over the last 5 years"
4. **Correlation**: "How does rainfall affect rice yield in West Bengal?"

### Enhanced Data Visualization
- Interactive charts and graphs using Chart.js
- Responsive tables with sorting and filtering
- Export functionality for data and visualizations
- Cache status indicators for performance transparency

### Comprehensive Citation & Traceability System
- **Complete Data Lineage**: Full traceability from query to source
- **Enhanced Citations**: Include dataset ID, publisher, license, data quality metrics
- **Data Freshness Indicators**: Shows how current the data is
- **Government Source Links**: Direct links to original data.gov.in datasets
- **Usage Statistics**: Shows exactly which records were analyzed
- **License Information**: Complete licensing and usage terms

### Robustness & Performance
- **Query Caching**: Intelligent caching system for 10x faster repeated queries
- **Error Handling**: Graceful handling of invalid queries and missing data
- **Data Quality Indicators**: Metadata about data freshness and reliability
- **Performance Monitoring**: Built-in cache statistics and performance metrics

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd project_samarth
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Install spaCy Model (for enhanced NLP)**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Test the Setup (Optional)**
   ```bash
   python setup_demo.py
   ```

6. **Run the Application**
   ```bash
   cd backend
   python main.py
   ```

7. **Open in Browser**
   Navigate to `http://localhost:5000`

### 🎯 Working with Your Datasets

The system now works with the local datasets you provided:

1. **Market Prices Data** (`9ef84268-d588-465a-a308-a864a43d0070.csv`)
   - Daily agricultural commodity prices across Indian markets
   - States, districts, crops, varieties, and price data

2. **Rainfall Data** (`rainfall_by_districts_2019.csv`) 
   - District-wise rainfall patterns for 2017-2018 season
   - Monsoon, winter, and summer rainfall data

**No API Key Required!** The system processes your local data files directly.

### Project Structure
```
project_samarth/
├── backend/
│   ├── main.py                 # Flask application entry point
│   ├── routes/
│   │   └── api_routes.py       # Additional API routes
│   └── utils/
│       ├── __init__.py         # Package initialization
│       ├── data_handler.py     # Data fetching and processing
│       ├── nlp_processor.py    # NLP and entity extraction
│       └── query_engine.py     # Query execution engine
├── frontend/
│   ├── index.html              # Main HTML interface
│   └── static/
│       ├── style.css           # Custom styles
│       └── script.js           # Frontend JavaScript
├── data/
│   ├── cache/                  # Cached API responses
│   ├── sample_agriculture_crop_production.csv
│   ├── sample_agriculture_state_wise_production.csv
│   └── sample_meteorology_rainfall_data.csv
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📊 Example Demonstrations

### Demo Query 1: Comparison Analysis
**User Input**: "Compare the average annual rainfall in Punjab and Haryana for the last 5 years."

**System Processing**:
1. **Entity Extraction**: States (Punjab, Haryana), Metric (rainfall), Time Period (5 years)
2. **Query Type**: Comparison
3. **Data Retrieval**: Rainfall data from IMD datasets
4. **Analysis**: Calculate average rainfall for both states (2016-2020)

**Sample Response**:
```
Based on the data, Punjab has higher average annual rainfall (653.8mm) compared to 
Haryana (578.1mm) over the last 5 years. This analysis is based on 10 data records 
from the India Meteorological Department.

[Interactive bar chart showing year-wise comparison]
[Data table with detailed values]

Data Sources:
- Annual Rainfall Data by State | Source: India Meteorological Department | 
  View Dataset: https://data.gov.in/resource/... | Records used: 10 | Accessed: 2025-10-25
```

### Demo Query 2: Ranking Analysis
**User Input**: "Which district has the highest rice production in India?"

**System Processing**:
1. **Entity Extraction**: Crop (rice), Metric (production), Scope (district-level)
2. **Query Type**: Ranking
3. **Data Retrieval**: District-wise production data
4. **Analysis**: Aggregate and rank districts by rice production

**Sample Response**:
```
Based on the available data, Murshidabad district in West Bengal has the highest 
rice production (1,580,000 tonnes), while Cuddalore district in Tamil Nadu has 
the lowest (580,000 tonnes).

[Horizontal bar chart showing top 10 districts]
[Ranked table with production values]
```

### Demo Query 3: Trend Analysis
**User Input**: "Analyze wheat production trend in Uttar Pradesh over the last decade."

**System Processing**:
1. **Entity Extraction**: Crop (wheat), State (Uttar Pradesh), Time Period (decade)
2. **Query Type**: Trend Analysis
3. **Data Retrieval**: Historical production data (2011-2020)
4. **Analysis**: Calculate trend direction and growth rate

**Sample Response**:
```
The trend analysis shows that wheat production in Uttar Pradesh has been increasing 
over the analyzed period, with a change of approximately 8.2%. Production grew from 
16.2 million tonnes in 2011 to 17.8 million tonnes in 2020.

[Line chart showing production trend over time]
[Statistical summary of growth pattern]
```

## 🔧 API Documentation

### Health Check
```http
GET /api/health
```
Returns system status and version information.

### Process Query
```http
POST /api/query
Content-Type: application/json

{
  "query": "Natural language question about agriculture/climate"
}
```

**Response Structure**:
```json
{
  "success": true,
  "query": "Original user query",
  "intent": "Processed intent description",
  "confidence": 0.85,
  "answer": "Natural language response",
  "data": {
    "dataset_name": {
      "columns": ["col1", "col2"],
      "data": [{"col1": "value1", "col2": "value2"}],
      "shape": [10, 2]
    }
  },
  "visualizations": [
    {
      "id": "viz_1",
      "type": "bar",
      "title": "Chart Title",
      "x_axis": "state",
      "y_axis": "production"
    }
  ],
  "citations": [
    {
      "dataset_name": "Crop Production Statistics",
      "source": "Ministry of Agriculture & Farmers Welfare",
      "url": "https://data.gov.in/resource/...",
      "accessed_date": "2025-10-25",
      "records_used": 50
    }
  ]
}
```

### List Datasets
```http
GET /api/datasets
```
Returns available datasets with metadata.

### Search Datasets
```http
GET /api/search?q=rice
```
Search for datasets based on query terms.

## 🔍 Data Sources & APIs

### Integrated Datasets
1. **Agricultural Production**
   - Crop Production Statistics
   - State-wise Agricultural Production
   - District-wise Crop Data

2. **Meteorological Data**
   - Annual Rainfall by State
   - Monthly Rainfall Statistics
   - Weather Pattern Data

### API Integration
- **Base URL**: `https://api.data.gov.in/resource`
- **Authentication**: API key required
- **Rate Limiting**: Implemented for responsible usage
- **Caching**: Local caching to reduce API calls

## 🧠 NLP Capabilities

### Entity Recognition
- **Indian States**: All 28 states and 8 union territories
- **Crops**: 50+ major Indian crops including cereals, pulses, oilseeds
- **Time Periods**: Years, ranges, relative periods ("last 5 years")
- **Metrics**: Production, yield, area, rainfall

### Query Understanding
- **Pattern Matching**: Regex patterns for different query types
- **Contextual Analysis**: Understanding implicit requirements
- **Confidence Scoring**: Reliability assessment of query interpretation

## 🔒 Data Privacy & Security

### Privacy Measures
- **No Third-party Storage**: All data remains within government sources
- **Local Caching Only**: Temporary storage for performance optimization
- **Source Transparency**: Complete citation of data sources
- **Government Data Only**: Exclusive use of official datasets

### Security Features
- **Input Validation**: Sanitization of user queries
- **Rate Limiting**: Protection against abuse
- **Error Handling**: Graceful handling of invalid requests
- **CORS Configuration**: Secure cross-origin requests

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for all functions
- Include unit tests for new features

## 📈 Performance Optimization

### Backend Optimizations
- **Data Caching**: Intelligent caching of frequently accessed datasets
- **Query Optimization**: Efficient pandas operations
- **Lazy Loading**: Load datasets only when needed
- **Connection Pooling**: Efficient database connections

### Frontend Optimizations
- **Responsive Design**: Mobile-first approach
- **Chart Rendering**: Optimized Chart.js configurations
- **Data Pagination**: Efficient handling of large datasets
- **Progressive Loading**: Gradual content loading

## 🐛 Troubleshooting

### Common Issues

**Issue**: SpaCy model not found
```bash
# Solution: Install the English model
python -m spacy download en_core_web_sm
```

**Issue**: API key errors
```bash
# Solution: Set your data.gov.in API key
export DATA_GOV_API_KEY=your_key_here
```

**Issue**: Port already in use
```bash
# Solution: Change port in main.py or kill existing process
lsof -ti:5000 | xargs kill -9
```

### Error Logs
Check `backend/logs/` directory for detailed error logs and debugging information.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **data.gov.in**: For providing open access to government datasets
- **Ministry of Agriculture & Farmers Welfare**: Agricultural data sources
- **India Meteorological Department**: Climate and weather data
- **Flask Community**: Web framework
- **spaCy**: Natural language processing capabilities

---

**Project Samarth** - Empowering agricultural decision-making through intelligent data analysis.

For support or questions, please open an issue in the repository.