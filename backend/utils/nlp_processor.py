"""
NLP Processing Module for Project Samarth
Handles natural language processing for query understanding and entity extraction
Uses spaCy and transformers for entity recognition and intent classification
"""

import spacy
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries supported by the system"""
    COMPARISON = "comparison"
    RANKING = "ranking"
    TREND_ANALYSIS = "trend_analysis"
    CORRELATION = "correlation"
    GENERAL_INFO = "general_info"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from user query"""
    entity_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class QueryAnalysis:
    """Complete analysis of user query"""
    query_type: QueryType
    entities: List[ExtractedEntity]
    intent: str
    confidence: float
    parameters: Dict[str, Any]

class NLPProcessor:
    """
    Main NLP processor for understanding agricultural and meteorological queries
    """
    
    def __init__(self):
        # Try to load spaCy model, fallback to basic processing if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.spacy_available = True
            logger.info("SpaCy model loaded successfully")
        except OSError:
            logger.warning("SpaCy model not found. Using basic NLP processing.")
            self.spacy_available = False
            self.nlp = None
        
        # Initialize entity patterns and mappings
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize regex patterns and entity mappings"""
        
        # Indian states and union territories
        self.indian_states = {
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
            'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya',
            'mizoram', 'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim',
            'tamil nadu', 'telangana', 'tripura', 'uttarakhand', 'uttar pradesh',
            'west bengal', 'delhi', 'jammu and kashmir', 'ladakh', 'chandigarh',
            'dadra and nagar haveli', 'daman and diu', 'lakshadweep', 'puducherry',
            'andaman and nicobar islands'
        }
        
        # Common crops in India
        self.indian_crops = {
            'rice', 'wheat', 'maize', 'barley', 'bajra', 'jowar', 'ragi',
            'sugarcane', 'cotton', 'jute', 'tea', 'coffee', 'coconut',
            'groundnut', 'sesame', 'rape', 'mustard', 'linseed', 'castor',
            'sunflower', 'safflower', 'niger', 'soybean', 'sesamum',
            'arhar', 'moong', 'urad', 'masoor', 'gram', 'khesari',
            'onion', 'potato', 'sweet potato', 'tapioca', 'banana',
            'mango', 'citrus', 'apple', 'grapes', 'pomegranate',
            'cashew', 'cardamom', 'black pepper', 'turmeric', 'ginger',
            'coriander', 'cumin', 'fennel', 'fenugreek'
        }
        
        # Query type patterns
        self.query_patterns = {
            QueryType.COMPARISON: [
                r'compare.*between|compare.*and|difference between|versus|vs',
                r'higher.*than|lower.*than|more.*than|less.*than',
                r'which.*better|which.*worse|which.*higher|which.*lower'
            ],
            QueryType.RANKING: [
                r'highest|lowest|maximum|minimum|top|bottom|best|worst',
                r'rank.*by|sort.*by|order.*by',
                r'which.*most|which.*least|leading|lagging'
            ],
            QueryType.TREND_ANALYSIS: [
                r'trend|pattern|over.*years?|over.*time|across.*years?',
                r'increase|increase|growth|decline|change',
                r'from.*to|between.*and.*year|during.*period'
            ],
            QueryType.CORRELATION: [
                r'correlat|relationship|connect|link|impact.*on',
                r'affect|influence|depend|relate',
                r'due.*to|because.*of|result.*of'
            ]
        }
        
        # Time period patterns
        self.time_patterns = {
            r'last (\d+) years?': lambda m: int(m.group(1)),
            r'past (\d+) years?': lambda m: int(m.group(1)),
            r'(\d{4})-(\d{4})': lambda m: (int(m.group(1)), int(m.group(2))),
            r'from (\d{4}) to (\d{4})': lambda m: (int(m.group(1)), int(m.group(2))),
            r'between (\d{4}) and (\d{4})': lambda m: (int(m.group(1)), int(m.group(2))),
            r'in (\d{4})': lambda m: int(m.group(1)),
            r'decade': lambda m: 10,
            r'last decade': lambda m: 10
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze user query to extract intent, entities, and parameters
        
        Args:
            query: Natural language query from user
            
        Returns:
            QueryAnalysis object with extracted information
        """
        query_lower = query.lower().strip()
        
        # Determine query type
        query_type = self._classify_query_type(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query, query_lower)
        
        # Extract parameters
        parameters = self._extract_parameters(query_lower)
        
        # Generate intent description
        intent = self._generate_intent(query_type, entities, parameters)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(query_type, entities, parameters)
        
        return QueryAnalysis(
            query_type=query_type,
            entities=entities,
            intent=intent,
            confidence=confidence,
            parameters=parameters
        )
    
    def _classify_query_type(self, query: str) -> QueryType:
        """Classify the type of query based on patterns"""
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return query_type
        
        return QueryType.GENERAL_INFO
    
    def _extract_entities(self, original_query: str, query_lower: str) -> List[ExtractedEntity]:
        """Extract entities from query using spaCy and pattern matching"""
        entities = []
        
        # Use spaCy if available
        if self.spacy_available and self.nlp:
            doc = self.nlp(original_query)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:  # Geographic entities
                    entities.append(ExtractedEntity(
                        entity_type='location',
                        value=ent.text,
                        confidence=0.8,
                        start_pos=ent.start_char,
                        end_pos=ent.end_char
                    ))
                elif ent.label_ == 'DATE':
                    entities.append(ExtractedEntity(
                        entity_type='date',
                        value=ent.text,
                        confidence=0.7,
                        start_pos=ent.start_char,
                        end_pos=ent.end_char
                    ))
        
        # Pattern-based entity extraction
        # Extract states
        for state in self.indian_states:
            pattern = r'\b' + re.escape(state) + r'\b'
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                entities.append(ExtractedEntity(
                    entity_type='state',
                    value=state.title(),
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Extract crops
        for crop in self.indian_crops:
            pattern = r'\b' + re.escape(crop) + r'\b'
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                entities.append(ExtractedEntity(
                    entity_type='crop',
                    value=crop.title(),
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Extract years
        year_pattern = r'\b(19|20)\d{2}\b'
        year_matches = re.finditer(year_pattern, query_lower)
        for match in year_matches:
            entities.append(ExtractedEntity(
                entity_type='year',
                value=match.group(),
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Remove duplicates and overlapping entities
        entities = self._remove_duplicate_entities(entities)
        
        return entities
    
    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract parameters like time periods, metrics, etc."""
        parameters = {}
        
        # Extract time periods
        for pattern, extractor in self.time_patterns.items():
            match = re.search(pattern, query)
            if match:
                parameters['time_period'] = extractor(match)
                break
        
        # Extract metrics
        if any(word in query for word in ['production', 'produce', 'output']):
            parameters['metric'] = 'production'
        elif any(word in query for word in ['rainfall', 'rain', 'precipitation']):
            parameters['metric'] = 'rainfall'
        elif any(word in query for word in ['yield', 'productivity']):
            parameters['metric'] = 'yield'
        elif any(word in query for word in ['area', 'acreage']):
            parameters['metric'] = 'area'
        
        # Extract aggregation type
        if any(word in query for word in ['average', 'mean', 'avg']):
            parameters['aggregation'] = 'mean'
        elif any(word in query for word in ['total', 'sum']):
            parameters['aggregation'] = 'sum'
        elif any(word in query for word in ['maximum', 'max', 'highest']):
            parameters['aggregation'] = 'max'
        elif any(word in query for word in ['minimum', 'min', 'lowest']):
            parameters['aggregation'] = 'min'
        
        return parameters
    
    def _remove_duplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate and overlapping entities"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x.start_pos)
        
        filtered_entities = []
        for entity in entities:
            # Check for overlaps with existing entities
            overlap = False
            for existing in filtered_entities:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    # Keep the entity with higher confidence
                    if entity.confidence > existing.confidence:
                        filtered_entities.remove(existing)
                        filtered_entities.append(entity)
                    overlap = True
                    break
            
            if not overlap:
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _generate_intent(self, query_type: QueryType, 
                        entities: List[ExtractedEntity],
                        parameters: Dict[str, Any]) -> str:
        """Generate human-readable intent description"""
        
        entity_dict = {}
        for entity in entities:
            if entity.entity_type not in entity_dict:
                entity_dict[entity.entity_type] = []
            entity_dict[entity.entity_type].append(entity.value)
        
        if query_type == QueryType.COMPARISON:
            states = entity_dict.get('state', [])
            crops = entity_dict.get('crop', [])
            metric = parameters.get('metric', 'production')
            
            if len(states) >= 2:
                return f"Compare {metric} between {' and '.join(states)}"
            elif crops and states:
                return f"Compare {crops[0]} {metric} across states"
            else:
                return f"Compare {metric} data"
        
        elif query_type == QueryType.RANKING:
            metric = parameters.get('metric', 'production')
            crops = entity_dict.get('crop', [])
            
            if crops:
                return f"Rank states by {crops[0]} {metric}"
            else:
                return f"Rank by {metric}"
        
        elif query_type == QueryType.TREND_ANALYSIS:
            crops = entity_dict.get('crop', [])
            states = entity_dict.get('state', [])
            metric = parameters.get('metric', 'production')
            
            if crops and states:
                return f"Analyze {crops[0]} {metric} trend in {states[0]}"
            elif crops:
                return f"Analyze {crops[0]} {metric} trend"
            else:
                return f"Analyze {metric} trend"
        
        elif query_type == QueryType.CORRELATION:
            return "Analyze correlation between agricultural and meteorological data"
        
        else:
            return "General agricultural or meteorological information query"
    
    def _calculate_confidence(self, query_type: QueryType,
                            entities: List[ExtractedEntity],
                            parameters: Dict[str, Any]) -> float:
        """Calculate confidence score for query analysis"""
        
        base_confidence = 0.5
        
        # Boost confidence based on entities found
        entity_boost = min(len(entities) * 0.1, 0.3)
        
        # Boost confidence based on parameters extracted
        param_boost = min(len(parameters) * 0.05, 0.15)
        
        # Boost confidence based on query type specificity
        type_boost = 0.1 if query_type != QueryType.GENERAL_INFO else 0.0
        
        confidence = base_confidence + entity_boost + param_boost + type_boost
        
        return min(confidence, 1.0)

class QueryMapper:
    """
    Maps analyzed queries to database operations
    """
    
    def __init__(self):
        self.dataset_mappings = {
            'production': {
                'datasets': ['agriculture.crop_production', 'agriculture.state_wise_production'],
                'key_columns': ['state', 'crop', 'year', 'production']
            },
            'rainfall': {
                'datasets': ['meteorology.rainfall_data', 'meteorology.monthly_rainfall'],
                'key_columns': ['state', 'year', 'rainfall']
            },
            'yield': {
                'datasets': ['agriculture.crop_production'],
                'key_columns': ['state', 'crop', 'year', 'yield']
            },
            'area': {
                'datasets': ['agriculture.crop_production'],
                'key_columns': ['state', 'crop', 'year', 'area']
            }
        }
    
    def map_query_to_operations(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Map query analysis to specific data operations
        
        Args:
            analysis: QueryAnalysis object
            
        Returns:
            Dictionary containing operation specifications
        """
        operations = {
            'query_type': analysis.query_type.value,
            'datasets_needed': [],
            'filters': {},
            'aggregations': [],
            'joins': [],
            'output_format': 'table'
        }
        
        # Determine required datasets based on metric
        metric = analysis.parameters.get('metric', 'production')
        if metric in self.dataset_mappings:
            operations['datasets_needed'] = self.dataset_mappings[metric]['datasets']
        
        # Build filters from entities
        for entity in analysis.entities:
            if entity.entity_type == 'state':
                if 'state' not in operations['filters']:
                    operations['filters']['state'] = []
                operations['filters']['state'].append(entity.value)
            elif entity.entity_type == 'crop':
                if 'crop' not in operations['filters']:
                    operations['filters']['crop'] = []
                operations['filters']['crop'].append(entity.value)
            elif entity.entity_type == 'year':
                if 'year' not in operations['filters']:
                    operations['filters']['year'] = []
                operations['filters']['year'].append(int(entity.value))
        
        # Handle time periods
        if 'time_period' in analysis.parameters:
            time_period = analysis.parameters['time_period']
            if isinstance(time_period, int):
                # Last N years
                import datetime
                current_year = datetime.datetime.now().year
                start_year = current_year - time_period
                operations['filters']['year_range'] = (start_year, current_year)
            elif isinstance(time_period, tuple):
                # Year range
                operations['filters']['year_range'] = time_period
        
        # Define aggregations based on query type and parameters
        agg_type = analysis.parameters.get('aggregation', 'sum')
        operations['aggregations'] = [{
            'column': metric,
            'function': agg_type,
            'group_by': ['state', 'year'] if analysis.query_type == QueryType.TREND_ANALYSIS else ['state']
        }]
        
        # Set output format based on query type
        if analysis.query_type in [QueryType.TREND_ANALYSIS, QueryType.CORRELATION]:
            operations['output_format'] = 'chart'
        elif analysis.query_type == QueryType.RANKING:
            operations['output_format'] = 'ranked_table'
        
        return operations